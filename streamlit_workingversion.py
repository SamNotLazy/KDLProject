import streamlit as st
import requests
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="India Geospatial Analysis")


# --- GitHub and Data Configuration ---
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/SamNotLazy/KDLProject/master/INDIAN-SHAPEFILES-master/"
GITHUB_API_BASE_URL = "https://api.github.com/repos/SamNotLazy/KDLProject/contents/"
BASE_DIR = 'Data/INDIAN-SHAPEFILES-master'


# --- Caching with Streamlit ---
# Use st.cache_data for functions that return serializable data objects (like lists, dataframes).
# ttl=3600 caches the result for 1 hour, similar to the original Dash app.
@st.cache_data(ttl=3600)
def get_state_names():
    """
    Fetches the complete list of state names (directory names) from the GitHub repository.
    """
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

            if 'next' in response.links:
                api_url = response.links['next']['url']
            else:
                api_url = None

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching directory contents from GitHub: {e}")
            return []

    return sorted(all_state_names)

@st.cache_data
def load_geo(relative_file_path: str):
    """
    Loads a geospatial file from a local path or downloads it from GitHub.
    """
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
        response = requests.get(github_url, stream=True)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return gpd.read_file(local_path)

    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}. Could not download from {github_url}.")
    except Exception as e:
        st.error(f"An unexpected error occurred while downloading: {e}")

    return None

# --- Charting Functions (mostly unchanged) ---
def calculate_zoom(gdf: gpd.GeoDataFrame, adjustment: int = 0) -> int:
    """Calculates an appropriate map zoom level."""
    if gdf.empty:
        return 8
    minx, miny, maxx, maxy = gdf.total_bounds
    width = maxx - minx
    height = maxy - miny
    if width == 0 or height == 0:
        return 12 + adjustment
    max_dim = max(width, height)
    zoom = np.floor(np.log2(360 / max_dim))
    return int(np.clip(zoom + adjustment, 1, 10))

def plot_charts(change_df, gdf, geo_key, color_scale, map_title, bar_title):
    """Creates a Plotly choropleth map and a bar chart."""
    plot_df = gdf.merge(change_df, left_on=geo_key, right_on=geo_key, how="left")
    plot_df = plot_df[plot_df["Change"].notnull()]

    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor='white', plot_bgcolor='white',
            annotations=[dict(text="No data to display", xref="paper", yref="paper", showarrow=False, font=dict(size=16))]
        )
        return fig, fig

    # --- Choropleth Map ---
    minx, miny, maxx, maxy = gdf.total_bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    map_fig = px.choropleth_mapbox(
        plot_df,
        geojson=plot_df.geometry,
        locations=plot_df.index,
        color="Change",
        hover_name=geo_key,
        hover_data={"Change": True},
        mapbox_style="carto-positron",
        center={"lat": center_lat, "lon": center_lon},
        zoom=calculate_zoom(gdf),
        opacity=0.7,
        color_continuous_scale=color_scale,
        labels={"Change": "Change"}
    )
    map_fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title={'text': map_title, 'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
        paper_bgcolor='white',
        font_color='black',
    )

    # --- Bar Chart ---
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
    return map_fig, bar_fig

# --- Main App Logic ---

# Initialize session state for view management
if 'view_level' not in st.session_state:
    st.session_state.view_level = 'state'
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None

# Create base directory if it doesn't exist
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok=True)

# --- UI Sidebar and Controls ---
with st.sidebar:
    st.header("Controls")
    state_list = get_state_names()
    if not state_list:
        st.error("Could not fetch state list from GitHub. Please check your connection.")
        st.stop()

    # When state dropdown changes, reset view to state level
    selected_state = st.selectbox(
        'Select a State',
        options=state_list,
        format_func=lambda x: x.replace('_', ' ').title(),
        index=0,
        key='state_selector',
        on_change=lambda: st.session_state.update(view_level='state', selected_district=None)
    )

    # --- View Logic ---
    if st.session_state.view_level == 'state':
        gdf_districts = load_geo(f'STATES/{selected_state}/{selected_state}_DISTRICTS.geojson')
        if gdf_districts is not None and 'dtname' in gdf_districts.columns:
            districts = sorted(gdf_districts['dtname'].unique())
            # Add a placeholder for the user to select a district to drill down
            districts.insert(0, "Select a district to view sub-districts...")

            # The district dropdown triggers the view change
            selected_district = st.selectbox(
                'Select a District',
                options=districts,
                index=0,
                key='district_selector'
            )
            # If a valid district is chosen, switch the view
            if selected_district != "Select a district to view sub-districts...":
                st.session_state.view_level = 'district'
                st.session_state.selected_district = selected_district
                st.rerun() # Rerun the script to show the district view
        else:
            st.warning(f"No district data available for {selected_state}.")

    elif st.session_state.view_level == 'district':
        # Provide a button to go back to the state view
        if st.button("⬅️ Back to State View"):
            st.session_state.view_level = 'state'
            st.session_state.selected_district = None
            st.rerun()

# --- Main Panel: Displaying Titles and Charts ---

if st.session_state.view_level == 'state':
    st.title(f"State View: {selected_state.replace('_', ' ').title()}")

    gdf_districts = load_geo(f'STATES/{selected_state}/{selected_state}_DISTRICTS.geojson')
    if gdf_districts is not None and 'dtname' in gdf_districts.columns:
        np.random.seed(42)
        df_random = pd.DataFrame({"dtname": gdf_districts["dtname"], "Change": np.random.uniform(-50, 100, len(gdf_districts))})

        map_title = f"District-wise Map of {selected_state.replace('_', ' ').title()}"
        bar_title = "District Data Comparison"
        map_fig, bar_fig = plot_charts(df_random, gdf_districts, "dtname", "RdYlGn", map_title, bar_title)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(map_fig, use_container_width=True)
        with col2:
            st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.error(f"Could not load district data for {selected_state}.")

elif st.session_state.view_level == 'district':
    district = st.session_state.selected_district
    st.title(f"Sub-District View: {district.title()}")

    gdf_subdistricts = load_geo(f'STATES/{selected_state}/{selected_state}_SUBDISTRICTS.geojson')

    if gdf_subdistricts is not None:
        gdf_filtered = gdf_subdistricts[gdf_subdistricts["dtname"].str.strip().str.lower() == district.strip().lower()]

        if not gdf_filtered.empty:
            np.random.seed(42) # Use same seed for consistent random data
            df_random = pd.DataFrame({"sdtname": gdf_filtered["sdtname"], "Change": np.random.uniform(0, 100, len(gdf_filtered))})

            map_title = f"Sub-District Map of {district.title()}"
            bar_title = f"Sub-District Data for {district.title()}"
            map_fig, bar_fig = plot_charts(df_random, gdf_filtered, "sdtname", "RdYlGn", map_title, bar_title)

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(map_fig, use_container_width=True)
            with col2:
                st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.warning(f"No sub-district data found for {district} in {selected_state}.")
    else:
        st.error(f"Could not load sub-district geo-data for {selected_state}.")