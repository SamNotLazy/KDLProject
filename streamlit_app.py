import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="India State Maps",
    page_icon="🗺️",
    layout="wide"
)


# --- Cached GeoJSON Loader ---
@st.cache_data
def load_geo(file_path):
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return None
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


# ************************************************************************


# --- Function to plot map and bar chart ---
def plot_charts(change_df, color_scale, map_title, bar_title):
    plot_df = change_df.copy()
    # st.write(plot_df)
    geo_key = st.session_state["geo_unit_col"]
    map_col = "Change"
    bar_col = "Change"

    GEO_COL = st.session_state["GEO_COL"]
    gdf = st.session_state["gdf"]

    # Merge shapefile with change data
    plot_df = gdf.merge(plot_df, left_on=GEO_COL, right_on=geo_key, how="left").copy()
    plot_df = plot_df[plot_df["Change"].notnull()]

    num_bars = len(plot_df)
    # st.write(num_bars)
    # 1. Get the geographic bounds
    minx, miny, maxx, maxy = gdf.total_bounds
    # st.write(minx,miny,maxx,maxy)

    # 2. Calculate the area of the bounding box
    width = abs(maxx - minx)
    height = abs(maxy - miny)

    # st.write(minx, miny, maxx, maxy, width, height)
    factor_padding = 0.05

    if width < 1.2 and height < 1.2:
        factor_padding = 0.001

    minx *= (1 - factor_padding)
    miny *= (1 - factor_padding)
    maxx *= (1 + factor_padding)
    maxy *= (1 + factor_padding)

    # st.write(minx, miny, maxx, maxy, width, height)


    if (width <= height):
            # st.write("width<=height")
            minx -= (height - width) / 2
            maxx += (height - width) / 2


    else:
        # st.write("width>height")
        # Dont need to add maxy (north)
        miny -= (width - height)/2

    width = abs(maxx - minx)
    height = abs(maxy - miny)
    # st.write(minx, miny, maxx, maxy,width, height, width/height)

    if width/height>1.68:
        minx -= (height - width) / 2
        maxx += (height - width) / 2
    width = abs(maxx - minx)
    height = abs(maxy - miny)
    # st.write(minx, miny, maxx, maxy,width, height, width/height)



    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # --- Choropleth Map ---
    map_fig = px.choropleth_mapbox(
        plot_df,
        geojson=plot_df.__geo_interface__,
        locations=plot_df.index,
        color=map_col,
        hover_name=geo_key,
        hover_data={map_col: True, bar_col: True},
        mapbox_style="white-bg",  # mapbox_style="carto-positron",
        opacity=0.7,
        color_continuous_scale=color_scale,
        labels={map_col: map_col},
        center={"lat": center_lat, "lon": center_lon},
        zoom=0  # overridden by bounds
    )

    # Add text labels
    map_fig.add_trace(go.Scattermapbox(
        lon=plot_df.geometry.centroid.x,
        lat=plot_df.geometry.centroid.y,
        mode='text',
        text=plot_df.apply(lambda row: f"{row[geo_key]}<br>{row[map_col]}", axis=1),
        textfont=dict(size=8, color='black'),
        hoverinfo='none'
    ))

    # Force map to fit bounds with dynamic padding
    factor_padding = 0.0001
    map_fig.update_mapboxes(
        bounds={
            "west": float(minx),
            "east": float(maxx),
            "south": float(miny),
            "north": float(maxy)
            #     lat/3 is also good estimate for maxy
        }
    )

    # map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    map_fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # mapbox_bounds=padded_bounds
        # height=800  # increase from default ~450
    )

    # --- Bar Chart ---
    bar_fig = px.bar(
        plot_df.sort_values(bar_col, ascending=True),
        x=bar_col, y=geo_key, orientation='h',
        title=bar_title,
        labels={geo_key: 'District', bar_col: bar_col},
        color=bar_col,
        color_continuous_scale=color_scale,
        height=max(400, num_bars * 25),
        text=plot_df[bar_col].round(2)
    )
    bar_fig.update_traces(
        texttemplate="%{text}",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=10, color="black"),
        cliponaxis=False
    )
    bar_fig.update_coloraxes(showscale=False)

    bar_fig.update_layout(
        # height=max(400, len(plot_df) * 25),
        margin=dict(l=0, r=0, t=50, b=0),
        yaxis=dict(tickfont=dict(size=10)),
        # height=num_bars*30,
    )

    selected_state = st.session_state["selected_state"]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"District Map of {selected_state.title()}")
        with st.container():
            st.plotly_chart(map_fig, use_container_height=True, zoom_level=-8)
    with col2:
        st.subheader("District Data")
        with st.container(height=400):
            st.plotly_chart(bar_fig, use_container_width=True, use_container_height=True)


# ***************************************************************************8

# --- UI Layout ---
st.title("🗺️ Interactive Choropleth Maps of India")
st.markdown("Select a state and upload a CSV with district-level data to visualize on the map.")

# --- State Selection ---
STATES_DIR = 'INDIAN-SHAPEFILES-master/STATES'
try:
    state_list = [name for name in os.listdir(STATES_DIR) if os.path.isdir(os.path.join(STATES_DIR, name))]
    state_list.sort()
except FileNotFoundError:
    st.error(f"Directory not found: '{STATES_DIR}'")
    state_list = []

if not state_list:
    st.stop()

selected_state = st.selectbox("**Select a State**", state_list)
st.session_state["selected_state"] = selected_state  # Needed by plot_charts()

# --- Load GeoData ---
geo_path = f'{STATES_DIR}/{selected_state}/{selected_state}_DISTRICTS.geojson'
gdf = load_geo(geo_path)
if gdf is None or gdf.empty:
    st.stop()

# Detect the district name column
geo_key = "dtname"
st.session_state["geo_unit_col"] = geo_key
st.session_state["GEO_COL"] = geo_key
st.session_state["gdf"] = gdf

# Create DataFrame with district name + "Change" column
df_random = pd.DataFrame({
    geo_key: gdf[geo_key],
    "Change": np.random.uniform(0, 100, len(gdf))  # Must be named "Change" for plot_charts()
})

# Call plot_charts()
plot_charts(df_random, "RdYlGn", "Random Value Map", "Random Value by District")
