import json
import os
import dash
from dash import dcc, html, Input, Output, State, no_update, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import config
from cache import cache
from data_loader import get_state_names, load_geo
from plotting import plot_charts, get_plotly_map_layout

# --- Assume these functions are defined elsewhere ---
# --- For this example to be runnable, we will create dummy versions ---


# --- Dash App and Cache Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
server = app.server

cache.init_app(app.server, config=config.CACHE_CONFIG)



state_list = get_state_names()

config.PLOTLY_CUSTOM_MAP_LAYOUTS={}





# --- Dash UI Layout ---
app.layout = dbc.Container(fluid=True, style={'backgroundColor': '#ffffff'}, children=[
    dcc.Interval(id='interval-update-width', interval=500, n_intervals=0),
    dcc.Store(id='view-level-store', data='state'),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='state-dropdown', options=[{'label': state.replace('_', ' ').title(), 'value': state} for state in state_list], value=state_list[0] if state_list else None, clearable=False)),
        dbc.Col(dbc.Button("Next State ➡️", id="next-state-button", className="w-100"), width="auto"),
        dbc.Col(dcc.Dropdown(id='district-dropdown', clearable=False), width="auto"),
        dbc.Col(dbc.Button("Next District ➡️", id="next-district-button", className="w-100"), width="auto"),
    ], className="my-4", justify="center"),
    html.Div(id='error-message', className="px-5"),
    html.Div(id='device-width-display', style={'textAlign': 'center', 'color': 'grey', 'fontStyle': 'italic', 'marginBottom': '15px'}),
    dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col(dbc.Button("⬅️ Back to State View", id="back-button", color="primary", outline=True, style={'display': 'none'}), width="auto"),
            dbc.Col(html.H3(id="view-title", className="text-center"), width=True),
        ], align="center", className="mb-3"), # Note: reduced margin-bottom

        # --- MODIFICATION START: Added a control panel for sliders ---
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Longitude (Left/Right)", className="fw-bold"),
                        dcc.Slider(id='lon-slider', min=-180, max=180, step=1, value=78.96, marks=None, tooltip={"placement": "bottom", "always_visible": True})
                    ], width=4),
                    dbc.Col([
                        html.Label("Latitude (Up/Down)", className="fw-bold"),
                        dcc.Slider(id='lat-slider', min=-90, max=90, step=1, value=20.59, marks=None, tooltip={"placement": "bottom", "always_visible": True})
                    ], width=4),
                    dbc.Col([
                        html.Label("Map Zoom", className="fw-bold"),
                        dcc.Slider(id='zoom-slider', min=4, max=15, step=0.5, value=6.5, marks={i: str(i) for i in range(4, 16)}, tooltip={"placement": "bottom", "always_visible": True})
                    ], width=4),
                ])
            ]),
            className="mb-4"
        ),
        # --- MODIFICATION END ---

        dbc.Row([
            dbc.Col(dcc.Graph(id='map-graph', style={'height': 'auto'}, config=config.MAP_CONFIG), lg=6),
            dbc.Col(html.Div(dcc.Graph(id='bar-graph'), style={'height': 'auto', 'overflowY': 'auto'}), lg=6),
        ]),
    ]), className="mb-4"),
])

# # --- Callbacks ---
# clientside_callback(
#     """
#     function(n_intervals) {
#         return `Device Available Width: ${window.innerWidth}px`;
#     }
#     """,
#     Output('device-width-display', 'children'),
#     Input('interval-update-width', 'n_intervals')
# )

@app.callback(
    # --- MODIFICATION: Added outputs for new sliders ---
    Output('map-graph', 'figure'),
    Output('bar-graph', 'figure'),
    Output('district-dropdown', 'options'),
    Output('district-dropdown', 'value'),
    Output('view-level-store', 'data'),
    Output('back-button', 'style'),
    Output('view-title', 'children'),
    Output('error-message', 'children'),
    Output('map-graph', 'clickData'),
    Output('state-dropdown', 'value'),
    Output('lon-slider', 'value'),
    Output('lat-slider', 'value'),
    # --- MODIFICATION: Added inputs for new sliders ---
    Input('state-dropdown', 'value'),
    Input('district-dropdown', 'value'),
    Input('map-graph', 'clickData'),
    Input('back-button', 'n_clicks'),
    Input('next-state-button', 'n_clicks'),
    Input('next-district-button', 'n_clicks'),
    Input('zoom-slider', 'value'),
    Input('lon-slider', 'value'),
    Input('lat-slider', 'value'),
    State('view-level-store', 'data'),
    State('state-dropdown', 'options'),
    State('district-dropdown', 'options')
)
def update_view(selected_state, selected_district, clickData, back_clicks,
                next_state_clicks, next_district_clicks,
                zoom_value, lon_value, lat_value,
                current_view, state_options, district_options):
    triggered_id = dash.ctx.triggered_id
    empty_fig = go.FigureWidget().update_layout(paper_bgcolor='white', plot_bgcolor='white', annotations=[dict(text="No data to display", xref="paper", yref="paper", showarrow=False, font=dict(size=16))])
    num_outputs = 12 # <-- Updated output count

    # Save the compiled metadata to a file

    with open("plotlycustommaplayoutmd.json", 'w') as f:
        json.dump(config.PLOTLY_CUSTOM_MAP_LAYOUTS, f, indent=4)

    # --- Helper function for state view ---
    def show_state_view(state):
        gdf_districts = load_geo(f'STATES/{state}/{state}_DISTRICTS.geojson')
        if gdf_districts is None or 'dtname' not in gdf_districts.columns:
            err_msg = dbc.Alert(f"Could not load district data for {state}.", "danger")
            return (empty_fig, empty_fig, [], None, 'state', {'display': 'none'}, f"Data for {state}", err_msg, None, state, no_update, no_update)

        # --- MODIFICATION: Logic to determine map center ---
        map_layout = get_plotly_map_layout(gdf_districts)
        center_lon, center_lat = map_layout["mapbox_center"]["lon"], map_layout["mapbox_center"]["lat"]
        # If a slider triggered the update, use its values instead of the default
        if triggered_id in ['lon-slider', 'lat-slider', 'zoom-slider']:
            center_lon, center_lat = lon_value, lat_value

        districts = sorted(gdf_districts['dtname'].unique())
        options = [{'label': d, 'value': d} for d in districts]
        value = districts[0] if districts else None
        np.random.seed(42)
        df_random = pd.DataFrame({"dtname": gdf_districts["dtname"], "Change": np.random.uniform(-50, 100, len(gdf_districts))})

        map_fig, bar_fig = plot_charts(df_random, gdf_districts, "dtname", "RdYlGn", f"District Map of {state.replace('_', ' ').title()}", "District Data Comparison", zoom=zoom_value)
        map_layout["mapbox_zoom"]=zoom_value
        map_fig.update_layout(
            mapbox_center={"lon": center_lon, "lat": center_lat},
        )
        config.PLOTLY_CUSTOM_MAP_LAYOUTS[state]={"districts":{}}
        config.PLOTLY_CUSTOM_MAP_LAYOUTS[state]['mapbox_center']={"lon": center_lon, "lat": center_lat}
        config.PLOTLY_CUSTOM_MAP_LAYOUTS[state]['mapbox_zoom']=zoom_value

        for i in districts:
            config.PLOTLY_CUSTOM_MAP_LAYOUTS[state]['districts'][i]={}

        print(config.PLOTLY_CUSTOM_MAP_LAYOUTS)


        title = f"State View: {state.replace('_', ' ').title()}"
        return (map_fig, bar_fig, options, value, 'state', {'display': 'none'}, title, None, None, state, center_lon, center_lat)

    # --- Helper function for sub-district view ---
    def show_subdistrict_view(state, district):
        gdf_subs = load_geo(f'STATES/{state}/{state}_SUBDISTRICTS.geojson')
        if gdf_subs is None:
            err_msg = dbc.Alert(f"Could not load sub-districts geo-data for {state}.", "danger")
            return (empty_fig, empty_fig, no_update, no_update, 'district', {'display': 'block'}, f"Sub-District View: {district}", err_msg, None, no_update, no_update, no_update)

        gdf_filtered = gdf_subs[gdf_subs["dtname"].str.strip().str.lower() == district.strip().lower()]
        if gdf_filtered.empty:
            err_msg = dbc.Alert(f"No sub-district data for {district}.", "warning")
            return (empty_fig, empty_fig, no_update, no_update, 'district', {'display': 'block'}, f"Sub-District View: {district}", err_msg, None, no_update, no_update, no_update)

        # --- MODIFICATION: Logic to determine map center ---
        map_layout = get_plotly_map_layout(gdf_filtered)
        map_layout["mapbox_zoom"]=zoom_value
        center_lon, center_lat = map_layout["mapbox_center"]["lon"], map_layout["mapbox_center"]["lat"]
        # If a slider triggered the update, use its values instead of the default
        if triggered_id in ['lon-slider', 'lat-slider', 'zoom-slider']:
            center_lon, center_lat = lon_value, lat_value

        np.random.seed(42)
        df_random = pd.DataFrame({"sdtname": gdf_filtered["sdtname"], "Change": np.random.uniform(0, 100, len(gdf_filtered))})
        map_fig, bar_fig = plot_charts(df_random, gdf_filtered, "sdtname", "RdYlGn", f"Sub-District Map of {district.title()}", f"Sub-District Data for {district.title()}", zoom=zoom_value)

        map_fig.update_layout(
            mapbox_center={"lon": center_lon, "lat": center_lat},
            uirevision=f"{state}-{district}",
            autosize=True
        )
        title = f"Sub-District View: {district.title()}"
        config.PLOTLY_CUSTOM_MAP_LAYOUTS[state]["districts"][district]['mapbox_center']={"lon": center_lon, "lat": center_lat}
        config.PLOTLY_CUSTOM_MAP_LAYOUTS[state]["districts"][district]['mapbox_center']['mapbox_zoom']=zoom_value
        print(config.PLOTLY_CUSTOM_MAP_LAYOUTS)
        print(district)
        return (map_fig, bar_fig, no_update, district, 'district', {'display': 'block'}, title, None, None, no_update, center_lon, center_lat)

    # --- Main callback logic ---

    if triggered_id == 'next-state-button':
        state_values = [opt['value'] for opt in state_options]
        try:
            current_index = state_values.index(selected_state)
            next_index = (current_index + 1) % len(state_values)
            new_state = state_values[next_index]
            return show_state_view(new_state)
        except (ValueError, IndexError): return [no_update] * num_outputs

    if triggered_id == 'next-district-button':
        district_values = [opt['value'] for opt in district_options]
        if not district_values: return [no_update] * num_outputs
        try:
            current_index = district_values.index(selected_district)
            next_index = (current_index + 1) % len(district_values)
            new_district = district_values[next_index]
            return show_subdistrict_view(selected_state, new_district)
        except (ValueError, IndexError): return [no_update] * num_outputs

    # If a slider is moved, redraw the current view with new settings
    if triggered_id in ['zoom-slider', 'lon-slider', 'lat-slider']:
        if current_view == 'state':
            return show_state_view(selected_state)
        elif current_view == 'district' and selected_district:
            return show_subdistrict_view(selected_state, selected_district)
        else:
            return show_state_view(selected_state)

    if triggered_id in ['state-dropdown', 'back-button'] or not triggered_id:
        return show_state_view(selected_state)

    if triggered_id == 'map-graph' and clickData and current_view == 'state':
        clicked_district = clickData['points'][0].get('customdata', '')
        if not clicked_district: clicked_district = clickData['points'][0].get('hovertext', '').split('<br>')[0]
        if clicked_district: return show_subdistrict_view(selected_state, clicked_district)

    if triggered_id == 'district-dropdown' and selected_district:
        return show_subdistrict_view(selected_state, selected_district)
    return [no_update] * num_outputs
# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)