import dash
from dash import dcc, html, Input, Output, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from flask_caching import Cache
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# from PlotlyMap import plot_charts
# --- Dash App and Cache Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Configure caching
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

# --- Cached GeoJSON Loader (Unchanged Signature) ---
@cache.memoize(timeout=3600)  # Cache for 1 hour
def load_geo(file_path):
    """
    Loads a GeoJSON file into a GeoDataFrame.
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

# --- Function to create map and bar chart ---
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
    minx, miny, maxx, maxy = gdf.total_bounds
    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2
    def create_Map():
        # --- Choropleth Map ---
        map_fig = px.choropleth_map(
            plot_df,
            geojson=plot_df.geometry,
            locations=plot_df.index,
            color=map_col,
            hover_name=geo_key,
            hover_data={map_col: True, bar_col: True},
            map_style="white-bg", # Using a different mapbox style for better visuals
            opacity=0.7,
            color_continuous_scale=color_scale,
            labels={map_col: map_col},
            center={"lat": center_lat, "lon": center_lon},
            zoom=5 # A sensible default zoom
        )

        # Add text labels
        map_fig.add_trace(go.Scattermapbox(
            lon=plot_df.geometry.centroid.x,
            lat=plot_df.geometry.centroid.y,
            mode='text',
            text=plot_df.apply(lambda row: f"{row[geo_key]}<br>{row[map_col]}", axis=1),
            textfont=dict(size=9, color='black'),
            hoverinfo='none'
        ))
        map_fig.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            title=map_title,
            paper_bgcolor='white',
            font_color='black'
        )
        return map_fig

    def create_Bar():
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
            text=bar_col
        )
        bar_fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
        )
        bar_fig.update_coloraxes(showscale=False)
        bar_fig.update_layout(
            margin=dict(l=10, r=50, t=50, b=10),
            yaxis=dict(tickfont=dict(size=10)),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font_color='black'
        )
        return bar_fig
    return create_Map(), create_Bar()










# --- App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
server = app.server

# --- Data Preparation and Configuration ---
BASE_DIR = 'INDIAN-SHAPEFILES-master'
STATES_DIR = os.path.join(BASE_DIR, 'STATES')

try:
    if os.path.exists(STATES_DIR):
        state_list = [name for name in os.listdir(STATES_DIR) if os.path.isdir(os.path.join(STATES_DIR, name))]
        state_list.sort()
    else:
        state_list = []
except Exception as e:
    print(f"Error accessing state directory at {STATES_DIR}: {e}")
    state_list = []







# --- Dash UI Layout ---
app.layout = dbc.Container(fluid=True, style={'backgroundColor': '#f8f9fa'}, children=[

    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': state, 'value': state} for state in state_list],
            value=state_list[0] if state_list else None,
            clearable=False,
            placeholder="Select a State"
        ), width={'size': 4, 'offset': 2}),
        dbc.Col(dcc.Dropdown(
            id='district-dropdown',
            clearable=False,
            placeholder="Select a District"
        ), width=4),
    ], className="mb-4 justify-content-center"),

    html.Div(id='error-message', className="px-5"),

    # --- State Level Visualization ---
    html.Div(id='state-view', children=[
        dbc.Card(dbc.CardBody([
            html.H3("State Level View", className="text-center mt-2 mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(id='state-map-graph', style={'height': '70vh'}), width=12, lg=7),
                dbc.Col(html.Div([
                    dcc.Graph(id='state-bar-graph', responsive=False)
                ], style={'height': '70vh', 'overflowY': 'auto'}), width=12, lg=5),
            ]),
        ]), className="mb-4"),
    ]),

    # --- Sub-District Level Visualization (Initially Hidden) ---
    html.Div(id='subdistrict-view', style={'display': 'none'}, children=[
        dbc.Card(dbc.CardBody([
            dbc.Row([
                dbc.Col(dbc.Button("⬅️ Back to State View", id="back-button", color="primary", outline=True), width="auto"),
                dbc.Col(html.H3("Sub-District Level View", className="text-center"), width=True),
            ], align="center", className="mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(id='subdistrict-map-graph', style={'height': '70vh'}), width=12, lg=7),
                dbc.Col(html.Div([
                    dcc.Graph(id='subdistrict-bar-graph', responsive=False)
                ], style={'height': '70vh', 'overflowY': 'auto'}), width=12, lg=5),
            ])
        ]), className="mb-4")
    ])
])

# --- Combined Callback for State Graphs and District Dropdown ---
@app.callback(
    Output('district-dropdown', 'options'),
    Output('district-dropdown', 'value'),
    Output('state-map-graph', 'figure'),
    Output('state-bar-graph', 'figure'),
    Input('state-dropdown', 'value')
)
def update_state_level(selected_state):
    """
    On state selection, this callback:
    1. Populates the district dropdown with districts of the selected state.
    2. Sets the dropdown's value to the first district.
    3. Generates and displays the state-level choropleth map and bar chart.
    """
    empty_fig = go.Figure()
    empty_fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', annotations=[dict(text="No data available", xref="paper", yref="paper", showarrow=False, font=dict(size=16))])

    if not selected_state:
        return [], None, empty_fig, empty_fig

    # Load district data
    districts_geo_path = f'{STATES_DIR}/{selected_state}/{selected_state}_DISTRICTS.geojson'
    gdf_districts = load_geo(districts_geo_path)
    if gdf_districts is None or 'dtname' not in gdf_districts.columns:
        return [], None, empty_fig, empty_fig

    # Update dropdown
    districts = sorted(gdf_districts['dtname'].unique())
    options = [{'label': district, 'value': district} for district in districts]
    value = districts[0] if districts else None

    # Generate random data and plots
    geo_key = "dtname"
    np.random.seed(42)
    df_random = pd.DataFrame({
        geo_key: gdf_districts[geo_key],
        "Change": np.random.uniform(-50, 100, len(gdf_districts))
    })

    map_fig, bar_fig = plot_charts(
        change_df=df_random, gdf=gdf_districts, geo_key=geo_key,
        color_scale="RdYlGn",
        map_title=f"District-wise Map of {selected_state.replace('_', ' ').title()}",
        bar_title="District Data Comparison"
    )
    return options, value, map_fig, bar_fig

# --- Callback to Toggle Between State and Sub-District Views ---
@app.callback(
    Output('state-view', 'style'),
    Output('subdistrict-view', 'style'),
    Output('district-dropdown', 'value', allow_duplicate=True),
    Output('state-map-graph', 'clickData'), # Output to reset clickData after use
    Input('state-map-graph', 'clickData'),
    Input('back-button', 'n_clicks'),
    Input('state-dropdown', 'value'),
    prevent_initial_call=True
)
def toggle_views(clickData, back_clicks, state_val):
    """
    Manages the visibility of state vs. sub-district views.
    - On district click: Hides state view, shows sub-district view, and updates district dropdown value.
    - On 'Back' button click or state change: Shows state view and hides sub-district view.
    """
    triggered_id = dash.ctx.triggered_id
    show = {'display': 'block'}
    hide = {'display': 'none'}

    if triggered_id == 'state-map-graph' and clickData:
        clicked_district = clickData['points'][0]['hovertext']
        return hide, show, clicked_district, None # Reset clickData

    elif triggered_id in ['back-button', 'state-dropdown']:
        return show, hide, dash.no_update, None # Reset clickData

    raise PreventUpdate


# --- Callback for Sub-District Level Graphs ---
@app.callback(
    Output('subdistrict-map-graph', 'figure'),
    Output('subdistrict-bar-graph', 'figure'),
    Output('error-message', 'children'),
    Input('state-dropdown', 'value'),
    Input('district-dropdown', 'value')
)
def update_subdistrict_graphs(selected_state, selected_district):
    """
    Generates and updates the sub-district-level map and bar chart
    based on the selected state and district. This is triggered when the
    district dropdown value changes (either by user or by clicking the map).
    """
    # Clear previous errors
    error_message = None

    empty_fig = go.Figure()
    empty_fig.update_layout(paper_bgcolor='white', plot_bgcolor='white', annotations=[dict(text="No data to display", xref="paper", yref="paper", showarrow=False, font=dict(size=16))])

    if not selected_state or not selected_district:
        return empty_fig, empty_fig, dbc.Alert("Please select a state and a district.", color="info")

    # Load sub-district data
    sub_districts_geo_path = f'{STATES_DIR}/{selected_state}/{selected_state}_SUBDISTRICTS.geojson'
    gdf_state_subdistricts = load_geo(sub_districts_geo_path)

    if gdf_state_subdistricts is None or gdf_state_subdistricts.empty:
        error_message = dbc.Alert(f"Could not load sub-districts geo-data for {selected_state}.", color="danger")
        return empty_fig, empty_fig, error_message

    # Filter for the selected district
    district_key, sub_district_key = "dtname", "sdtname"
    gdf_filtered = gdf_state_subdistricts[
        (gdf_state_subdistricts[district_key].str.strip().str.lower() == selected_district.strip().lower())
    ]

    if gdf_filtered.empty:
        error_message = dbc.Alert(f"No sub-district data found for {selected_district}, {selected_state}.", color="warning")
        return empty_fig, empty_fig, error_message

    # Generate random data and plots
    np.random.seed(42)
    df_random = pd.DataFrame({
        sub_district_key: gdf_filtered[sub_district_key],
        "Change": np.random.uniform(0, 100, len(gdf_filtered))
    })

    map_fig, bar_fig = plot_charts(
        change_df=df_random, gdf=gdf_filtered, geo_key=sub_district_key,
        color_scale="Viridis",
        map_title=f"Sub-District Map of {selected_district.title()}",
        bar_title=f"Sub-District Data for {selected_district.title()}"
    )
    return map_fig, bar_fig, error_message

# --- Run the App ---
if __name__ == '__main__':
    if not os.path.exists(BASE_DIR):
        print("="*50)
        print("ERROR: 'INDIAN-SHAPEFILES-master' directory not found.")
        print("Please download and unzip them from:")
        print("https://github.com/datameet/INDIAN-SHAPEFILES/archive/refs/heads/master.zip")
        print(f"And ensure the '{BASE_DIR}' directory is in the same folder as this script.")
        print("="*50)
    else:
        app.run(debug=True)
