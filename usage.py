# ruff: noqa: E501
import json
import textwrap

import altair as alt
from dash import Dash, Input, Output, callback, dcc, html
from vega_datasets import data

import dash_vega_components as dvc

app = Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)


app.layout = html.Div(
    [
        html.H1("Demo of dash-vega-components", id="header1"),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Vega-Altair charts",
                    children=[
                        dcc.Markdown(
                            textwrap.dedent(
                                """\
                            You can pass any [Vega-Altair](https://altair-viz.github.io/) chart to `dash_vega_components.Vega` by
                            converting it to a dictionary using `chart.to_dict()`. You
                            can use the interactivity of Altair itself or update other
                            components on the page using callbacks which can read out
                            the current state of the chart.
                            """
                            )
                        ),
                        dcc.Dropdown(
                            ["All", "USA", "Europe", "Japan"],
                            "All",
                            id="origin-dropdown",
                            style={"width": "400px"},
                        ),
                        dvc.Vega(
                            id="altair-chart",
                            signalsToObserve=[
                                "circle_size",
                                "legend_origin",
                                "brush_selection",
                            ],
                        ),
                        dcc.Markdown(
                            textwrap.dedent(
                                """\
                            You can read out any parameter/signal of a chart. Try the following and observe how the dictionary below changes:

                            * change the 'Circle size' above
                            * click on an entry in the legend
                            * select a region in the chart (the numbers you see below are the lower and upper bounds of the selection)
                            """
                            )
                        ),
                        html.Div(id="altair-params"),
                        dcc.Markdown(
                            "You can pass various options for the rendering. For example, you can change the renderer to SVG and scale the chart keeping the original proportions",
                            style={"marginTop": "40px"},
                        ),
                        html.Div(
                            dcc.Slider(
                                0.5,
                                2,
                                step=0.25,
                                value=1.25,
                                id="svg-renderer-scale-factor-slider",
                            ),
                            style={"width": "400px"},
                        ),
                        dvc.Vega(
                            id="altair-chart-scaled",
                            opt={"renderer": "svg", "actions": False},
                            svgRendererScaleFactor=1.3,
                        ),
                        dcc.Markdown(
                            "Make the chart responsive by setting `width='container'` on the Altair chart and `style={'width': '100%'}` on the `Vega` component. Resize your window to see the effect. Notice that you can also read out the width of the chart if you want.",
                            style={"marginTop": "20px"},
                        ),
                        html.Div(
                            dvc.Vega(
                                id="altair-chart-width",
                                style={"width": "100%"},
                                signalsToObserve=[
                                    "width",
                                    "circle_size",
                                    "legend_origin",
                                ],
                            ),
                        ),
                        html.Div("No value so far", id="altair-width-params"),
                    ],
                ),
                dcc.Tab(
                    label="Vega and Vega-Lite charts",
                    children=[
                        dcc.Markdown(
                            """
                            [Vega](https://vega.github.io/vega/) and [Vega-Lite](https://vega.github.io/vega-lite/) charts work in exactly the same way and support
                            the same features as Vega-Altair charts.
                            """
                        ),
                        html.H3("Vega chart"),
                        html.Div(
                            "Example taken from https://vega.github.io/vega/examples/earthquakes/"
                        ),
                        dvc.Vega(id="vega-chart"),
                        html.H3("Vega-Lite chart"),
                        html.Div(
                            "Example taken from https://vega.github.io/vega-lite/examples/interactive_multi_line_pivot_tooltip.html"
                        ),
                        dvc.Vega(id="vega-lite-chart"),
                    ],
                ),
            ]
        ),
    ]
)


@callback(
    Output("altair-params", "children"),
    Input("altair-chart", "signalData"),
    prevent_initial_call=True,
)
def display_altair_params(params):
    return json.dumps(params, indent=2)


@callback(
    Output("altair-width-params", "children"),
    Input("altair-chart-width", "signalData"),
    prevent_initial_call=True,
)
def display_altair_width_params(params):
    return json.dumps(params)


@callback(
    Output("altair-chart", "spec"),
    Input("origin-dropdown", "value"),
)
def display_altair_chart_1(origin):
    chart = make_chart(origin, add_circle_size_slider=True, add_histogram=True)
    return chart.to_dict()


@callback(
    Output("altair-chart-scaled", "spec"),
    Output("altair-chart-scaled", "svgRendererScaleFactor"),
    Input("svg-renderer-scale-factor-slider", "value"),
)
def display_altair_chart_2(svgRendererScaleFactor):
    chart = make_chart("All", False)
    return chart.to_dict(), svgRendererScaleFactor


@callback(
    Output("altair-chart-width", "spec"),
    Input("header1", "children"),
)
def display_altair_chart_3(_):
    chart = make_chart("All", True)
    # This can also be passed directly when intantiating the chart, e.g.
    # alt.Chart(..., width="container")
    chart = chart.properties(width="container")
    return chart.to_dict()


def make_chart(origin: str, add_circle_size_slider: bool, add_histogram: bool = False):
    source = data.cars()

    if origin != "All":
        source = source[source["Origin"] == origin]

    legend_origin = alt.selection_point(
        fields=["Origin"], bind="legend", name="legend_origin"
    )

    if add_circle_size_slider:
        circle_size = alt.param(
            value=60,
            name="circle_size",
            bind=alt.binding_range(min=10, max=100, step=5, name="Circle size"),
        )
    else:
        circle_size = alt.Undefined

    chart = (
        alt.Chart(source)
        .mark_circle(size=circle_size)
        .encode(
            x="Horsepower",
            y="Miles_per_Gallon",
            color=alt.Color("Origin").scale(domain=["Europe", "Japan", "USA"]),
            tooltip=["Name", "Origin", "Horsepower", "Miles_per_Gallon"],
            opacity=alt.condition(legend_origin, alt.value(0.8), alt.value(0.2)),
        )
        .add_params(legend_origin)
    )
    if add_circle_size_slider:
        chart = chart.add_params(circle_size)

    if add_histogram:
        brush = alt.selection_interval(name="brush_selection")
        chart = chart.add_params(brush)
        bars = (
            alt.Chart(source)
            .mark_bar()
            .encode(y="Origin:N", color="Origin:N", x="count(Origin):Q")
            .transform_filter(brush)
        )
        chart = chart & bars
    return chart


@callback(Output("vega-lite-chart", "spec"), Input("header1", "children"))
def display_vega_lite_chart(_):
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "url": "https://raw.githubusercontent.com/vega/vega-datasets/main/data/stocks.csv"
        },
        "width": 400,
        "height": 300,
        "encoding": {"x": {"field": "date", "type": "temporal"}},
        "layer": [
            {
                "encoding": {
                    "color": {"field": "symbol", "type": "nominal"},
                    "y": {"field": "price", "type": "quantitative"},
                },
                "layer": [
                    {"mark": "line"},
                    {
                        "transform": [{"filter": {"param": "hover", "empty": False}}],
                        "mark": "point",
                    },
                ],
            },
            {
                "transform": [
                    {"pivot": "symbol", "value": "price", "groupby": ["date"]}
                ],
                "mark": "rule",
                "encoding": {
                    "opacity": {
                        "condition": {"value": 0.3, "param": "hover", "empty": False},
                        "value": 0,
                    },
                    "tooltip": [
                        {"field": "AAPL", "type": "quantitative"},
                        {"field": "AMZN", "type": "quantitative"},
                        {"field": "GOOG", "type": "quantitative"},
                        {"field": "IBM", "type": "quantitative"},
                        {"field": "MSFT", "type": "quantitative"},
                    ],
                },
                "params": [
                    {
                        "name": "hover",
                        "select": {
                            "type": "point",
                            "fields": ["date"],
                            "nearest": True,
                            "on": "mouseover",
                            "clear": "mouseout",
                        },
                    }
                ],
            },
        ],
    }


@callback(Output("vega-chart", "spec"), Input("header1", "children"))
def display_vega_chart(_):
    return {
        "$schema": "https://vega.github.io/schema/vega/v5.json",
        "description": "An interactive globe depicting earthquake locations and magnitudes.",
        "padding": 10,
        "width": 450,
        "height": 450,
        "autosize": "none",
        "signals": [
            {
                "name": "quakeSize",
                "value": 6,
                "bind": {"input": "range", "min": 0, "max": 12},
            },
            {
                "name": "rotate0",
                "value": 90,
                "bind": {"input": "range", "min": -180, "max": 180},
            },
            {
                "name": "rotate1",
                "value": -5,
                "bind": {"input": "range", "min": -180, "max": 180},
            },
        ],
        "data": [
            {"name": "sphere", "values": [{"type": "Sphere"}]},
            {
                "name": "world",
                "url": "https://raw.githubusercontent.com/vega/vega-datasets/main/data/world-110m.json",
                "format": {"type": "topojson", "feature": "countries"},
            },
            {
                "name": "earthquakes",
                "url": "https://raw.githubusercontent.com/vega/vega-datasets/main/data/earthquakes.json",
                "format": {"type": "json", "property": "features"},
            },
        ],
        "projections": [
            {
                "name": "projection",
                "scale": 225,
                "type": "orthographic",
                "translate": {"signal": "[width/2, height/2]"},
                "rotate": [{"signal": "rotate0"}, {"signal": "rotate1"}, 0],
            }
        ],
        "scales": [
            {
                "name": "size",
                "type": "sqrt",
                "domain": [0, 100],
                "range": [0, {"signal": "quakeSize"}],
            }
        ],
        "marks": [
            {
                "type": "shape",
                "from": {"data": "sphere"},
                "encode": {
                    "update": {
                        "fill": {"value": "aliceblue"},
                        "stroke": {"value": "black"},
                        "strokeWidth": {"value": 1.5},
                    }
                },
                "transform": [{"type": "geoshape", "projection": "projection"}],
            },
            {
                "type": "shape",
                "from": {"data": "world"},
                "encode": {
                    "update": {
                        "fill": {"value": "mintcream"},
                        "stroke": {"value": "black"},
                        "strokeWidth": {"value": 0.35},
                    }
                },
                "transform": [{"type": "geoshape", "projection": "projection"}],
            },
            {
                "type": "shape",
                "from": {"data": "earthquakes"},
                "encode": {
                    "update": {"opacity": {"value": 0.25}, "fill": {"value": "red"}}
                },
                "transform": [
                    {
                        "type": "geoshape",
                        "projection": "projection",
                        "pointRadius": {
                            "expr": "scale('size', exp(datum.properties.mag))"
                        },
                    }
                ],
            },
        ],
    }


if __name__ == "__main__":
    app.run_server(debug=True)
