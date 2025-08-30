# plotting.py
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

# The calculate_zoom function is no longer needed, as mapbox_bounds handles this automatically.

def plot_charts(change_df, gdf, geo_key, color_scale, map_title, bar_title,zoom=0):
    """
    Creates and returns a Plotly choropleth map and a bar chart.
    """
    # Merge shapefile with change data
    plot_df = gdf.merge(change_df, left_on=geo_key, right_on=geo_key, how="left")
    plot_df = plot_df[plot_df["Change"].notnull()]

    if plot_df.empty:
        return go.FigureWidget(), go.FigureWidget()


    # --- Choropleth Map ---
    map_fig = px.choropleth_mapbox(
        plot_df,
        geojson=plot_df.geometry,
        locations=plot_df.index,
        color="Change",
        hover_name=geo_key,
        mapbox_style="white-bg", # A good token-free style
        opacity=0.7,
        color_continuous_scale=color_scale,
        # center=map_layout["mapbox_center"],
        zoom=zoom

        # REMOVED zoom and center to allow mapbox_bounds to take control
    )
    map_fig.add_trace(go.Scattermapbox(
        lon=plot_df.geometry.centroid.x,
        lat=plot_df.geometry.centroid.y,
        mode='text',
        text=plot_df.apply(lambda row: f"{row[geo_key]}<br>{row['Change']:.2f}", axis=1),
        textfont=dict(size=9, color='black'),
        hoverinfo='none'
    ))
    map_fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text=map_title,
        title_x=0.5,
        paper_bgcolor='white',
        font_color='black',
        # ADDED mapbox_bounds to automatically fit the map to the data
        # mapbox_bounds=map_layout["mapbox_bounds"],
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
        height=num_bars * 25,
        text="Change",
    )
    bar_fig.update_traces(texttemplate="%{text:.2f}", textposition="auto")
    bar_fig.update_coloraxes(showscale=False)
    bar_fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(tickfont=dict(size=9), title=""),
        xaxis=dict(title="Change"),
        title_x=0.5,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black',
    )
    return map_fig, bar_fig



def get_rectangular_bounds(gdf):
    """
    Calculates the minimal rectangular bounding box of a GeoDataFrame.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame with a 'geometry' column.

    Returns:
        tuple: A tuple containing (min_lon, min_lat, max_lon, max_lat).
               Returns (None, None, None, None) if the GeoDataFrame is empty.
    """
    if gdf.empty:
        return None, None, None, None
    # total_bounds returns an array: [minx, miny, maxx, maxy]
    bounds = gdf.total_bounds
    return tuple(bounds)

def get_square_bounds(bounds, padding_factor=1.1):
    """
    Converts a rectangular bounding box to a padded square bounding box.

    It expands the shorter side to match the longer side, keeping the
    center point the same. It then applies a padding factor to increase
    the size of the square. This is useful for map displays to ensure
    features aren't right at the edge of the view.

    Args:
        bounds (tuple): A tuple containing (min_lon, min_lat, max_lon, max_lat).
        padding_factor (float, optional): The factor by which to increase
                                          the size of the square box.
                                          Defaults to 1.1 (a 10% padding).
                                          A value of 1.0 means no padding.

    Returns:
        tuple: A tuple for the padded square bounds (min_lon, min_lat,
               max_lon, max_lat). Returns the original bounds if they
               are invalid.
    """
    min_lon, min_lat, max_lon, max_lat = bounds
    if any(v is None for v in bounds):
        return bounds

    # Calculate spans and center
    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    # Determine the side length of the square and apply padding
    max_span = max(lon_span, lat_span)
    padded_span = max_span * padding_factor
    half_span = padded_span / 2

    # Calculate new square coordinates
    sq_min_lon = center_lon - half_span
    sq_max_lon = center_lon + half_span
    sq_min_lat = center_lat - half_span
    sq_max_lat = center_lat + half_span

    return (sq_min_lon, sq_min_lat, sq_max_lon, sq_max_lat)


def get_plotly_map_layout(gdf):
    """
    Calculates center, zoom, and bounds for a Plotly mapbox layout.

    This is the main helper function to use. It takes a GeoDataFrame,
    calculates the ideal square bounding box, and returns a dictionary
    of layout parameters ready to be used with `fig.update_layout()`.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame.

    Returns:
        dict: A dictionary with 'mapbox_center', 'mapbox_zoom', and
              'mapbox_bounds' keys, formatted for a Plotly Figure.
    """
    if gdf.empty:
        return {
            "mapbox_center": {'lat': 0, 'lon': 0},
            "mapbox_zoom": 1,
            "mapbox_bounds": None
        }

    # 1. Get rectangular bounds
    rect_bounds = get_rectangular_bounds(gdf)

    # 2. Convert to square bounds for better map fitting
    square_bounds = get_square_bounds(rect_bounds)
    min_lon, min_lat, max_lon, max_lat = square_bounds

    # 3. Format bounds into the dictionary format Plotly expects
    bounds_dict = {
        "west": min_lon,
        "south": min_lat,
        "east": max_lon,
        "north": max_lat
    }

    # 4. Calculate center from square bounds
    center = {
        'lat': (min_lat + max_lat) / 2,
        'lon': (min_lon + max_lon) / 2
    }

    # 5. Calculate zoom from square bounds
    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat
    if lon_span <= 0 or lat_span <= 0:
        zoom = 15
    else:
        max_span = max(lon_span, lat_span)
        zoom = int(round(np.interp(max_span, [0, 360], [18, 1])))

    # 6. Return the complete layout dictionary
    return {
        "mapbox_center": center,
        "mapbox_zoom": zoom,
        "mapbox_bounds": bounds_dict
    }


# --- Example Usage ---
if __name__ == "__main__":
    # This block allows you to test the script directly
    # 1. Create a sample GeoDataFrame
    long_thin_polygon = Polygon([
        (-122.4, 37.7),
        (-122.5, 37.7),
        (-122.5, 37.9),
        (-122.4, 37.9),
        (-122.4, 37.7)
    ])

    data = {'City': ['Test Area'], 'geometry': [long_thin_polygon]}
    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

    print("--- Testing get_plotly_map_layout ---")

    # 2. Get the layout dictionary
    map_layout = get_plotly_map_layout(gdf)

    print("\nLayout dictionary ready for Plotly:")
    # print(map_layout)
