import streamlit as st
import requests
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point

# --- Page Configuration ---
# Use the wide layout to give the top controls more space
st.set_page_config(layout="wide", page_title="India Geospatial Analysis")

# --- GitHub and Data Configuration ---
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/SamNotLazy/KDLProject/master/INDIAN-SHAPEFILES-master/"
GITHUB_API_BASE_URL = "https://api.github.com/repos/SamNotLazy/KDLProject/contents/"
BASE_DIR = 'Data/INDIAN-SHAPEFILES-master'

# --- Caching with Streamlit ---
@st.cache_data(ttl=3600)
def get_state_names():
    """Fetches the complete list of state names from the GitHub repository."""
    api_url = GITHUB_API_BASE_URL + 'INDIAN-SHAPEFILES-master/STATES'
    all_state_names = []
    while api_url:
        try:
            response = requests.get(api_url, params={'per_page': 100})
            response.raise_for_status()
            contents = response.json()
            if not isinstance(contents, list):
                st.error(f"Error: Expected a list from GitHub API, but got {type(contents)}")
                return []
            page_states = [item['name'] for item in contents if item.get('type') == 'dir']
            all_state_names.extend(page_states)
            api_url = response.links.get('next', {}).get('url')
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching directory contents from GitHub: {e}")
            return []
    return sorted(all_state_names)

@st.cache_data
def load_geo(relative_file_path: str):
    """Loads a geospatial file from a local path or downloads it from GitHub."""
    local_path = os.path.join(BASE_DIR, relative_file_path)
    github_url = GITHUB_RAW_BASE_URL + relative_file_path.replace("\\", "/")
    if os.path.exists(local_path):
        try:
            return gpd.read_file(local_path)
        except Exception as e:
            st.error(f"Error reading local file {local_path}: {e}")
            return None
    st.info(f"Downloading data from GitHub: {github_url}")
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with requests.get(github_url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return gpd.read_file(local_path)
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading or reading file from GitHub: {e}")
    return None

# --- Charting and Helper Functions ---
def find_polygon_from_click(gdf: gpd.GeoDataFrame, lat: float, lng: float, name_col: str):
    """Finds the name of the polygon that contains the clicked coordinates."""
    clicked_point = Point(lng, lat)
    for index, row in gdf.iterrows():
        if row['geometry'].contains(clicked_point):
            return row[name_col]
    return None

def plot_charts(change_df, gdf, geo_key, color_scale, map_title, bar_title):
    """Creates a Folium choropleth map on a forced white background and a Plotly bar chart."""
    plot_df = gdf.merge(change_df, left_on=geo_key, right_on=geo_key, how="left")
    plot_df = plot_df[plot_df["Change"].notnull()]

    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles=None,
                   scroll_wheel_zoom=False,
                   dragging=False,
                   zoom_control=False)

    white_background_geojson = {
        "type": "Polygon",
        "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]]
    }
    folium.GeoJson(
        white_background_geojson,
        name='white_background',
        style_function=lambda x: {'fillColor': 'white', 'color': 'white', 'weight': 1, 'fillOpacity': 1}
    ).add_to(m)

    if plot_df.empty:
        bar_fig = go.Figure()
        bar_fig.update_layout(
            paper_bgcolor='white', plot_bgcolor='white',
            annotations=[dict(text="No data to display", xref="paper", yref="paper", showarrow=False, font=dict(size=16))]
        )
        return m, bar_fig

    # --- NEW APPROACH ---
    # 1. Create the Choropleth object, but DON'T add it to the map yet.
    choropleth = folium.Choropleth(
        geo_data=plot_df,
        name='Choropleth',
        data=plot_df,
        columns=[geo_key, "Change"],
        key_on=f"feature.properties.{geo_key}",
        fill_color='RdYlGn',
        fill_opacity=0.7,
        line_opacity=0.4,
    )

    # 2. Find and remove the colormap from the choropleth's own children.
    for key in list(choropleth._children.keys()):
        if key.startswith('color_map'):
            del choropleth._children[key]

    # 3. Now, add the modified choropleth object to the map.
    choropleth.add_to(m)
    # --- END OF NEW APPROACH ---


    # Add permanent labels to the map
    for _, r in plot_df.iterrows():
        if r['geometry'] and r['geometry'].is_valid:
            lat = r['geometry'].centroid.y
            lon = r['geometry'].centroid.x
            label_text = r[geo_key]
            label_icon = folium.features.DivIcon(
                icon_size=(150, 36),
                icon_anchor=(75, 18),
                html=f'''<div style="font-size: 8pt; font-weight: 500; color: #212121; text-align: center; white-space: nowrap; text-shadow: 1px 1px 2px #FFFFFF, -1px -1px 2px #FFFFFF;">
                            {label_text}
                         </div>'''
            )
            folium.Marker(
                location=[lat, lon],
                icon=label_icon
            ).add_to(m)

    minx, miny, maxx, maxy = plot_df.total_bounds
    m.fit_bounds([[miny, minx], [maxy, maxx]])

    bar_df_sorted = plot_df.sort_values("Change", ascending=True)
    num_bars = len(bar_df_sorted)
    bar_fig = px.bar(
        bar_df_sorted,
        x="Change", y=geo_key, orientation='h',
        title=bar_title,
        color="Change",
        color_continuous_scale=color_scale,
        height=max(400, num_bars * 25),
        text="Change",
    )
    bar_fig.update_traces(texttemplate="%{text:.2f}", textposition="auto")
    bar_fig.update_coloraxes(showscale=False)
    bar_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(tickfont=dict(size=9)),
        paper_bgcolor='white', plot_bgcolor='white', font_color='black',
        title={'text': bar_title, 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
    )
    return m, bar_fig
# --- Main App Logic ---
# Initialize session state variables
if 'view_level' not in st.session_state:
    st.session_state.view_level = 'state'
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok=True)

# --- NEW: UI Controls at the Top of the Page ---

# Create columns for the selection widgets
control_col1, control_col2 = st.columns(2)

with control_col1:
    state_list = get_state_names()
    if not state_list:
        st.error("Could not fetch state list from GitHub. Please check your connection.")
        st.stop()

    selected_state = st.selectbox(
        'Select a State',
        options=state_list,
        format_func=lambda x: x.replace('_', ' ').title(),
        # Default to Karnataka if available
        index=state_list.index('KARNATAKA') if 'KARNATAKA' in state_list else 0,
        key='state_selector',
        # Reset the view to state level whenever a new state is chosen
        on_change=lambda: st.session_state.update(view_level='state', selected_district=None)
    )

with control_col2:
    # This column will either show the district drill-down or the 'Back' button
    if st.session_state.view_level == 'state':
        gdf_districts = load_geo(f'STATES/{selected_state}/{selected_state}_DISTRICTS.geojson')
        if gdf_districts is not None and 'dtname' in gdf_districts.columns:
            districts = sorted(gdf_districts['dtname'].unique())
            districts.insert(0, "Select a district to view sub-districts...")
            selected_district_from_dropdown = st.selectbox(
                'Select a District to Drill Down',
                options=districts,
                index=0,
                key='district_selector',
                help="Select a district here or click one on the map to see sub-districts."
            )
            # If the user selects a valid district, change the view level
            if selected_district_from_dropdown != "Select a district to view sub-districts...":
                st.session_state.view_level = 'district'
                st.session_state.selected_district = selected_district_from_dropdown
                st.rerun() # Rerun the script to update the view
        else:
            st.warning(f"No district data available for {selected_state}.")

    elif st.session_state.view_level == 'district':
        # Provide a clear indicator of the current view and a button to go back
        st.info(f"Viewing sub-districts for **{st.session_state.selected_district}**.")
        if st.button("⬅️ Back to State View"):
            st.session_state.view_level = 'state'
            st.session_state.selected_district = None
            st.rerun() # Rerun the script to go back to the state view

# Add a divider to visually separate controls from the content
st.divider()

# --- Main Panel: Displaying Titles and Charts ---
if st.session_state.view_level == 'state':
    gdf_districts = load_geo(f'STATES/{selected_state}/{selected_state}_DISTRICTS.geojson')
    if gdf_districts is not None and 'dtname' in gdf_districts.columns:
        # Generate random data for demonstration
        np.random.seed(42)
        df_random = pd.DataFrame({"dtname": gdf_districts["dtname"], "Change": np.random.uniform(-50, 100, len(gdf_districts))})
        map_title = f"District-wise Map of {selected_state.replace('_', ' ').title()}"
        bar_title = "District Data Comparison"
        folium_map, bar_fig = plot_charts(df_random, gdf_districts, "dtname", "RdYlGn", map_title, bar_title)

        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.subheader(map_title)
            map_data = st_folium(folium_map, use_container_width=True)
            st.write(map_data)
            if map_data and map_data.get("last_clicked"):
                lat, lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
                clicked_district = find_polygon_from_click(gdf_districts, lat, lng, "dtname")
                if clicked_district:
                    st.session_state.view_level = 'district'
                    st.session_state.selected_district = clicked_district
                    st.rerun()
                else:
                    st.warning("You clicked outside of any district boundary.")
        with col2:
            st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.error(f"Could not load district data for {selected_state}.")

elif st.session_state.view_level == 'district':
    district = st.session_state.selected_district
    gdf_subdistricts = load_geo(f'STATES/{selected_state}/{selected_state}_SUBDISTRICTS.geojson')
    if gdf_subdistricts is not None:
        gdf_filtered = gdf_subdistricts[gdf_subdistricts["dtname"].str.strip().str.lower() == district.strip().lower()]
        if not gdf_filtered.empty:
            np.random.seed(42)
            df_random = pd.DataFrame({"sdtname": gdf_filtered["sdtname"], "Change": np.random.uniform(0, 100, len(gdf_filtered))})
            map_title = f"Sub-District Map of {district.title()}"
            bar_title = f"Sub-District Data for {district.title()}"
            folium_map, bar_fig = plot_charts(df_random, gdf_filtered, "sdtname", "RdYlGn", map_title, bar_title)

            col1, col2 = st.columns([0.6, 0.4])
            with col1:
                st.subheader(map_title)
                map_data = st_folium(folium_map, use_container_width=True)
                st.write(map_data)

            if map_data and map_data.get("last_clicked"):
                    lat, lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
                    clicked_sdt = find_polygon_from_click(gdf_filtered, lat, lng, "sdtname")
                    if clicked_sdt:
                        st.success(f"🗺️ You clicked on: **{clicked_sdt}**")
                    else:
                        st.warning("You clicked outside of any sub-district boundary.")
            with col2:
                st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.warning(f"No sub-district data found for {district} in {selected_state}.")
    else:
        st.error(f"Could not load sub-district geo-data for {selected_state}.")