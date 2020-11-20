# Dash import
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

# HoloViews imports
import holoviews as hv
from holoviews.element.tiles import StamenTerrain
from holoviews.operation import histogram
from holoviews.operation.datashader import datashade
from holoviews.plotting.plotly.dash import to_dash
from holoviews.selection import link_selections

# Dash import
import dask.dataframe as dd

# Datashader colorscale import
from datashader.colors import Hot


# Set plot width
plot_width = int(750)
plot_height = int(plot_width//1.2)

# Find bounding box using http://bboxfinder.com/
x_range, y_range = (-8251262.5478, -8218623.9368), (4963419.3224, 4987496.9864)

plot_options = hv.Options(
    width=plot_width, height=plot_height,
)


usecols = [
    'dropoff_x', 'dropoff_y', 'pickup_x', 'pickup_y',
    'dropoff_hour', 'pickup_hour', 'passenger_count', 'fare_amount'
]


df = dd.read_csv(
    "/media/jmmease/ExtraDrive1/datashader/datashader-examples/data/nyc_taxi.csv",
).persist()

ds = hv.Dataset(df.compute())
# ds = hv.Dataset(df)

# import cudf
# ds = hv.Dataset(cudf.from_pandas(df.compute()))

# import dask_cudf
# ds = hv.Dataset(dask_cudf.from_dask_dataframe(df))

# Add more descriptive labels
ds = ds.redim.label(fare_amount="Fare Amount")

points = hv.Points(ds, ['dropoff_x', 'dropoff_y'])
shaded = datashade(points, cmap=Hot)
# tiles = StamenTerrain().redim.range(x=x_range, y=y_range).opts(height=700, width=700)
tiles = hv.Tiles("").redim.range(x=x_range, y=y_range).opts(
    accesstoken='pk.eyJ1Ijoiam1tZWFzZSIsImEiOiJjamljeWkwN3IwNjEyM3FtYTNweXV4YmV0In0.2zbgGCjbPTK7CToIg81kMw',
    mapboxstyle="dark",
    width=800, height=800
)

hist = histogram(
    ds, dimension="fare_amount", normed=False, num_bins=20, bin_range=(0, 30.0)
).opts(width=400)

lnk_sel = link_selections.instance()
linked_map = lnk_sel(tiles * shaded)
# linked_map = lnk_sel(shaded)
linked_hist = lnk_sel(hist)


# Create Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

components = to_dash(
    app,
    [linked_map, linked_hist],
    reset_button=True,
    button_class=dbc.Button,
)

# graph1 = components.graphs[0]
# graph2 = components.graphs[1]


app.layout = dbc.Container([
    html.H1("NYC Taxi Demo"),
    dbc.Row([
        dbc.Col(children=[
            dbc.Card([
                dbc.CardHeader("Drop off locations"),
                dbc.CardBody(children=[
                    components.graphs[0],
                ])
            ]),
        ]),
        dbc.Col(children=[
            dbc.Card([
                dbc.CardHeader("Histogram"),
                dbc.CardBody(children=[
                    components.graphs[1]
                ])
            ]),
        ])]
    ),
    components.resets[0],
    components.store,
])

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=True, port=8068)
