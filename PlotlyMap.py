import dash
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask_caching import Cache
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# --- Dash App and Cache Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
server = app.server

# Configure caching
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

# --- Cached GeoJSON Loader ---
@cache.memoize(timeout=3600)  # Cache for 1 hour
def load_geo(file_path):
    """
    Loads a GeoJSON file into a GeoDataFrame, with caching.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# --- Charting Function ---
def calculate_zoom(gdf: gpd.GeoDataFrame, adjustment: int = 0) -> int:
    """
    Calculates an appropriate map zoom level for a district-sized GeoDataFrame.

    Args:
        gdf: The GeoDataFrame for the district.
        adjustment: An integer to fine-tune the zoom.
                    - Use `1` to zoom in one level deeper.
                    - Use `-1` to zoom out one level.
                    - Default is `0` (no adjustment).

    Returns:
        An integer representing the final zoom level.
    """
    if gdf.empty:
        return 8 # A reasonable default for an unknown district

    minx, miny, maxx, maxy = gdf.total_bounds
    width = maxx - minx
    height = maxy - miny

    # If it's a single point (e.g., district HQ), zoom to a city/town level
    if width == 0 or height == 0:
        return 12 + adjustment

    max_dim = max(width, height)

    # Calculate the base zoom level
    zoom = np.floor(np.log2(360 / max_dim))

    # Apply the adjustment and clamp the result to a practical range
    final_zoom = int(np.clip(zoom + adjustment, 1, 10))

    return final_zoom
def plot_charts(change_df, gdf, geo_key, color_scale, map_title, bar_title):
    """
    Creates and returns a Plotly choropleth map and a bar chart.
    """
    plot_df = change_df.copy()
    map_col = "Change"
    bar_col = "Change"

    # Merge shapefile with change data
    plot_df = gdf.merge(plot_df, left_on=geo_key, right_on=geo_key, how="left").copy()
    plot_df = plot_df[plot_df["Change"].notnull()]

    if plot_df.empty:
        return go.Figure(), go.Figure()

    num_bars = len(plot_df)
    # --- Calculate maximum bounding square ---
    minx, miny, maxx, maxy = gdf.total_bounds
    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # Get the width and height of the bounding box
    width = maxx - minx
    height = maxy - miny

    # The side of the square is the larger of the two dimensions
    max_dim = max(width, height)

    # Add a 5% padding to the square's dimension
    padding = max_dim * 0.05

    # Calculate the new square bounds
    minx_sq = center_lon - (max_dim / 2) - padding
    maxx_sq = center_lon + (max_dim / 2) + padding
    miny_sq = center_lat - (max_dim / 2) - padding
    maxy_sq = center_lat + (max_dim / 2) + padding

    # --- Choropleth Map ---
    map_fig = px.choropleth_map(
        plot_df,
        geojson=plot_df.geometry,
        locations=plot_df.index,
        color=map_col,
        hover_name=geo_key,
        hover_data={map_col: True, bar_col: True},
        map_style="white-bg", # Using a token-free map style
        opacity=0.7,
        color_continuous_scale=color_scale,
        labels={map_col: map_col},
        center={"lat": center_lat, "lon": center_lon},
        zoom=calculate_zoom(gdf) # A sensible default zoom
    )

    map_fig.add_trace(go.Scattermap(
        lon=plot_df.geometry.centroid.x,
        lat=plot_df.geometry.centroid.y,
        mode='text',
        text=plot_df.apply(lambda row: f"{row[geo_key]}<br>{row[map_col]}", axis=1),
        textfont=dict(size=9, color='black'),
        hoverinfo='none'
    ))


    # CORRECTED: Removed the invalid properties that caused the ValueError.
    map_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title=map_title,
        paper_bgcolor='white',
        font_color='black',
        mapbox_bounds={"west": minx_sq, "east": maxx_sq, "south": miny_sq, "north": maxy_sq},
    )

    # --- Bar Chart ---
    bar_df_sorted = plot_df.sort_values(bar_col, ascending=True).copy()
    bar_fig = px.bar(
        bar_df_sorted,
        x=bar_col, y=geo_key, orientation='h',
        title=bar_title,
        labels={geo_key: 'District', bar_col: bar_col},
        color=bar_col,
        color_continuous_scale=color_scale,
        height=max(400, num_bars * 25), # Dynamically set height
        text=bar_col,
    )
    bar_fig.update_traces(
        texttemplate="%{text:.5f}",
        textposition="auto",
    )
    bar_fig.update_coloraxes(showscale=False)
    bar_fig.update_layout(
        margin=dict(l=20, r=0, t=0, b=0),
        # padding=dict(r=10),
        yaxis=dict(tickfont=dict(size=9)),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black',
    )
    return map_fig, bar_fig

# --- Data Preparation ---
BASE_DIR = 'INDIAN-SHAPEFILES-master'
STATES_DIR = os.path.join(BASE_DIR, 'STATES')
state_list = sorted([name for name in os.listdir(STATES_DIR) if os.path.isdir(os.path.join(STATES_DIR, name))]) if os.path.exists(STATES_DIR) else []

# --- Dash UI Layout ---
map_config = {'scrollZoom': True, 'displayModeBar': True, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}

app.layout = dbc.Container(fluid=True, style={'backgroundColor': '#ffffff'}, children=[
    # Store component to hold the current view level ('state' or 'district')
    dcc.Store(id='view-level-store', data='state'),

    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in state_list],
            value=state_list[0] if state_list else None,
            clearable=False
        ), width={'size': 4, 'offset': 2}),
        dbc.Col(dcc.Dropdown(id='district-dropdown', clearable=False), width=4),
    ], className="my-4 justify-content-center"),

    html.Div(id='error-message', className="px-5"),

    # --- CONSOLIDATED VIEW ---
    dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col(dbc.Button("⬅️ Back to State View", id="back-button", color="primary", outline=True, style={'display': 'none'}), width="auto"),
            dbc.Col(html.H3(id="view-title", className="text-center"), width=True),
        ], align="center", className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id='map-graph', style={'height': '70vh'}, config=map_config), lg=6),
            dbc.Col(
                html.Div(
                    dcc.Graph(id='bar-graph', responsive=False),
                    # Add padding and margin to the style dictionary below
                    style={
                        'height': '70vh',
                        'overflowY': 'auto',

                    }
                ),
                lg=6
            ),
        ]),
    ]), className="mb-4"),
])

# --- UNIFIED CALLBACK to manage all updates ---
@app.callback(
    Output('map-graph', 'figure'),
    Output('bar-graph', 'figure'),
    Output('district-dropdown', 'options'),
    Output('district-dropdown', 'value'),
    Output('view-level-store', 'data'),
    Output('back-button', 'style'),
    Output('view-title', 'children'),
    Output('error-message', 'children'),
    Output('map-graph', 'clickData'), # To reset clickData
    Input('state-dropdown', 'value'),
    Input('district-dropdown', 'value'),
    Input('map-graph', 'clickData'),
    Input('back-button', 'n_clicks'),
    State('view-level-store', 'data')
)
def update_view(selected_state, selected_district, clickData, back_clicks, current_view):
    """
    This single callback handles all logic:
    - Displays state-level data.
    - Drills down to sub-district level on map click or district dropdown change.
    - Returns to state-level on 'back' button click or state change.
    """
    triggered_id = dash.ctx.triggered_id
    error_message = None
    empty_fig = go.Figure()
    empty_fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', annotations=[dict(text="No data to display", xref="paper", yref="paper", showarrow=False, font=dict(size=16))])

    # --- LOGIC FOR STATE VIEW ---
    def show_state_view(state):
        gdf_districts = load_geo(f'{STATES_DIR}/{state}/{state}_DISTRICTS.geojson')
        if gdf_districts is None or 'dtname' not in gdf_districts.columns:
            return empty_fig, empty_fig, [], None, 'state', {'display': 'none'}, f"Data for {state}", dbc.Alert("Could not load district data.", "danger"), None

        districts = sorted(gdf_districts['dtname'].unique())
        options = [{'label': d, 'value': d} for d in districts]
        value = districts[0] if districts else None

        np.random.seed(42)
        df_random = pd.DataFrame({"dtname": gdf_districts["dtname"], "Change": np.random.uniform(-50, 100, len(gdf_districts))})

        map_fig, bar_fig = plot_charts(df_random, gdf_districts, "dtname", "RdYlGn",
                                       f"District-wise Map of {state.replace('_', ' ').title()}", "District Data Comparison")

        return map_fig, bar_fig, options, value, 'state', {'display': 'none'}, f"State View: {state.replace('_', ' ').title()}", None, None

    # --- LOGIC FOR SUB-DISTRICT VIEW ---
    def show_subdistrict_view(state, district):
        gdf_state_subdistricts = load_geo(f'{STATES_DIR}/{state}/{state}_SUBDISTRICTS.geojson')
        if gdf_state_subdistricts is None:
            return empty_fig, empty_fig, no_update, no_update, 'district', {'display': 'block'}, f"Sub-District View: {district}", dbc.Alert(f"Could not load sub-districts geo-data for {state}.", "danger"), None

        gdf_filtered = gdf_state_subdistricts[gdf_state_subdistricts["dtname"].str.strip().str.lower() == district.strip().lower()]
        if gdf_filtered.empty:
            return empty_fig, empty_fig, no_update, no_update, 'district', {'display': 'block'}, f"Sub-District View: {district}", dbc.Alert(f"No sub-district data for {district}.", "warning"), None

        np.random.seed(42)
        df_random = pd.DataFrame({"sdtname": gdf_filtered["sdtname"], "Change": np.random.uniform(0, 100, len(gdf_filtered))})

        map_fig, bar_fig = plot_charts(df_random, gdf_filtered, "sdtname", "RdYlGn",
                                       f"Sub-District Map of {district.title()}", f"Sub-District Data for {district.title()}")

        return map_fig, bar_fig, no_update, district, 'district', {'display': 'block'}, f"Sub-District View: {district.title()}", None, None

    # --- DETERMINE ACTION BASED ON TRIGGER ---
    if triggered_id in ['state-dropdown', 'back-button']:
        return show_state_view(selected_state)

    if triggered_id == 'map-graph' and clickData and current_view == 'state':
        # print(clickData)
        if 'hovertext' in clickData['points'][0]:
            clicked_district = clickData['points'][0]['hovertext'].split("<br>")[0]
            return show_subdistrict_view(selected_state, clicked_district)
        else:
            clicked_district = clickData['points'][0]['text'].split("<br>")[0]
            return show_subdistrict_view(selected_state, clicked_district)



    if triggered_id == 'district-dropdown' and selected_district:
        return show_subdistrict_view(selected_state, selected_district)

    if not triggered_id: # Initial load
        return show_state_view(selected_state)

    raise PreventUpdate

# --- Run the App ---
if __name__ == '__main__':
    if not os.path.exists(BASE_DIR):
        print("="*50)
        print("ERROR: 'INDIAN-SHAPEFILES-master' directory not found.")
        print("Please download and unzip it from:")
        print("https://github.com/datameet/INDIAN-SHAPEFILES/archive/refs/heads/master.zip")
        print(f"And ensure the '{BASE_DIR}' directory is in the same folder as this script.")
        print("="*50)
    else:
        app.run(debug=True)
