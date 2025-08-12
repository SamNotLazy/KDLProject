import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="All India State Maps",
    page_icon="🗺️",
    layout="wide"
)

# --- Cached GeoJSON Loader ---
@st.cache_data
def load_geo(file_path):
    """Loads a GeoJSON file from the given path."""
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return None
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except Exception as e:
        st.error(f"Error reading file {file_path}: {e}")
        return None

# --- Function to plot map and bar chart (User's Original Logic) ---
def plot_charts(state_name, gdf, change_df, district_col, color_scale):
    """
    Generates and displays a choropleth map and a bar chart for a given state
    using the user's original map design and bounds calculation.
    """
    map_col = "Change"
    bar_col = "Change"

    # Merge shapefile with change data
    plot_df = gdf.merge(change_df, left_on=district_col, right_on=district_col, how="left")
    plot_df = plot_df[plot_df["Change"].notnull()].copy()

    if plot_df.empty:
        st.warning(f"No data to display for {state_name.title()}.")
        return

    num_bars = len(plot_df)

    # --- User's Original Map Bounds Calculation Logic ---
    minx, miny, maxx, maxy = gdf.total_bounds
    width = abs(maxx - minx)
    height = abs(maxy - miny)
    factor_padding = 0.05

    if width < 1.2 and height < 1.2:
        factor_padding = 0.001

    minx *= (1 - factor_padding)
    miny *= (1 - factor_padding)
    maxx *= (1 + factor_padding)
    maxy *= (1 + factor_padding)

    if (width <= height):
        minx -= (height - width) / 2
        maxx += (height - width) / 2
    else:
        miny -= (width - height) / 2

    width = abs(maxx - minx)
    height = abs(maxy - miny)

    if width / height > 1.68:
        minx -= (height - width) / 2
        maxx += (height - width) / 2

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # --- Choropleth Map ---
    map_fig = px.choropleth_mapbox(
        plot_df,
        geojson=plot_df.__geo_interface__,
        locations=plot_df.index,
        color=map_col,
        hover_name=district_col,
        hover_data={map_col: True, bar_col: True},
        mapbox_style="white-bg",
        opacity=0.7,
        color_continuous_scale=color_scale,
        labels={map_col: map_col},
        center={"lat": center_lat, "lon": center_lon},
        zoom=0  # This will be overridden by the bounds
    )

    # Add text labels
    map_fig.add_trace(go.Scattermapbox(
        lon=plot_df.geometry.centroid.x,
        lat=plot_df.geometry.centroid.y,
        mode='text',
        text=plot_df.apply(lambda row: f"{row[district_col]}<br>{row[map_col]}", axis=1),
        textfont=dict(size=8, color='black'),
        hoverinfo='none'
    ))

    # Force map to fit bounds
    map_fig.update_mapboxes(
        bounds={
            "west": float(minx), "east": float(maxx),
            "south": float(miny), "north": float(maxy)
        }
    )
    map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # --- Bar Chart ---
    bar_fig = px.bar(
        plot_df.sort_values(bar_col, ascending=True),
        x=bar_col, y=district_col, orientation='h',
        title=f"Data for {state_name.title()}",
        labels={district_col: 'District', bar_col: bar_col},
        color=bar_col,
        color_continuous_scale=color_scale,
        height=max(400, num_bars * 25),
        text=plot_df[bar_col].round(2)
    )
    bar_fig.update_traces(
        texttemplate="%{text}", textposition="inside",
        insidetextanchor="middle", textfont=dict(size=10, color="black"),
        cliponaxis=False
    )
    bar_fig.update_coloraxes(showscale=False)
    bar_fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        yaxis=dict(tickfont=dict(size=10)),
    )

    # --- Display Charts in Columns ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"District Map of {state_name.title()}")
        st.plotly_chart(map_fig, use_container_width=True)
    with col2:
        st.subheader("District Data")
        st.plotly_chart(bar_fig, use_container_width=True)

# ***************************************************************************

# --- Main Application ---
st.title("🗺️ Interactive Choropleth Maps of India")
st.markdown("This application displays district-level data for all available states.")

# --- State Data Directory ---
STATES_DIR = 'INDIAN-SHAPEFILES-master/STATES'
try:
    state_list = [name for name in os.listdir(STATES_DIR) if os.path.isdir(os.path.join(STATES_DIR, name))]
    state_list.sort()
except FileNotFoundError:
    st.error(f"Main state directory not found: '{STATES_DIR}'")
    st.stop()

if not state_list:
    st.warning("No state folders found in the directory.")
    st.stop()

# --- Loop Through Each State and Plot ---
for state_name in state_list:
    st.header(f"📍 {state_name.replace('_', ' ').title()}")

    geo_path = f'{STATES_DIR}/{state_name}/{state_name}_DISTRICTS.geojson'
    gdf = load_geo(geo_path)

    if gdf is None or gdf.empty:
        continue

    district_col_name = "dtname"
    if district_col_name not in gdf.columns:
        st.error(f"District column '{district_col_name}' not found for {state_name}. Skipping.")
        continue

    df_random = pd.DataFrame({
        district_col_name: gdf[district_col_name],
        "Change": np.random.uniform(0, 100, len(gdf))
    })

    # Call the plotting function for the current state
    plot_charts(
        state_name=state_name,
        gdf=gdf,
        change_df=df_random,
        district_col=district_col_name,
        color_scale="RdYlGn" # Using your original color scale
    )

    st.divider()