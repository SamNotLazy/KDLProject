import plotly.express as px
import plotly.graph_objects as go

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

    # --- Choropleth Map ---
    map_fig = px.choropleth(
        plot_df,
        geojson=plot_df.geometry,
        locations=plot_df.index,
        color=map_col,
        hover_name=geo_key,
        hover_data={map_col: True, bar_col: True},
        projection="mercator", # Switched to a standard projection
        color_continuous_scale=color_scale,
        labels={map_col: map_col}
    )
    map_fig.update_geos(fitbounds="locations", visible=False)
    map_fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title=map_title,
        paper_bgcolor='white',
        font_color='black'
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

    return map_fig, bar_fig