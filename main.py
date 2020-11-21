# Dash import
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc

# HoloViews imports
import holoviews as hv
from holoviews.element.tiles import CartoLight, CartoDark, CartoEco
from holoviews.operation import histogram
from holoviews.operation.datashader import datashade
from holoviews.plotting.plotly.dash import to_dash
from holoviews.selection import link_selections

# Datashader colorscale import
import pandas as pd
from datashader.colors import Hot
import plotly.io as pio
from plotly import colors
# bgcolor = "rgba(0,0,0,0.03)"
# pio.templates["plotly_dark"].layout.update(paper_bgcolor=bgcolor, plot_bgcolor=bgcolor)
pio.templates.default = "plotly_white"

# Find bounding box using http://bboxfinder.com/
x_range, y_range = (-8251262.5478, -8218623.9368), (4963419.3224, 4987496.9864)
usecols = ['dropoff_x', 'dropoff_y', 'passenger_count', 'fare_amount']

df = pd.read_csv("/media/jmmease/ExtraDrive1/datashader/datashader-examples/data/nyc_taxi.csv")
# ds = hv.Dataset(df)

import cudf
ds = hv.Dataset(cudf.from_pandas(df))

# Add more descriptive labels
ds = ds.redim.label(fare_amount="Fare Amount")

points = hv.Points(ds, ['dropoff_x', 'dropoff_y'])
shaded = datashade(points, cmap=colors.sequential.Plasma)
tiles = CartoLight().redim.range(x=x_range, y=y_range).opts(height=800, width=800)

hist = histogram(
    ds, dimension="fare_amount", normed=False, num_bins=20, bin_range=(0, 30.0)
).opts(color=colors.qualitative.Plotly[0])

lnk_sel = link_selections.instance()
linked_map = lnk_sel(tiles * shaded)
linked_hist = lnk_sel(hist)

# Use plot hook to set the default drag mode to box selection
def set_dragmode(plot, element):
    fig = plot.state
    fig['layout']['dragmode'] = "select"
    fig['layout']['selectdirection'] = "h"

linked_hist.opts(hv.opts.Histogram(hooks=[set_dragmode]))
linked_hist.opts(margins=(60, 40, 30, 30))
linked_map.opts(margins=(30, 30, 30, 30))
# (left, bottom, right, top)
# Create Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

components = to_dash(
    app, [linked_map, linked_hist], reset_button=True, button_class=dbc.Button,
)

app.layout = dbc.Container([
    html.H1("NYC Taxi Demo", style={"padding-top": 40}),
    html.H3("Crossfiltering with Dash, Datashader, and HoloViews"),
    html.Hr(),
    dbc.Row([
        dbc.Col(children=[dbc.Card([
            dbc.CardHeader("Drop off locations"),
            dbc.CardBody(children=[
                components.graphs[0],
            ])])]),
        dbc.Col(children=[dbc.Card([
            dbc.CardHeader("Fair Amount"),
            dbc.CardBody(children=[
                components.graphs[1]
            ])])])
    ]),
    html.Div(style={"margin-top": 10}, children=components.resets[0]),
    components.store,
])

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=True, port=8068)
