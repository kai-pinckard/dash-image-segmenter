import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from components import *


external_scripts = [
    "https://code.jquery.com/jquery-3.3.1.slim.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js",
]

external_stylesheets = [
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
                ],
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        header(),
        html.Div(
            id="main-content",
            children=[],
            className="container-fluid",
        ) 
    ],
    className="container-fluid",
    )


@app.callback(dash.dependencies.Output('main-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def update_page(pathname):
    """
    This function is called whenever the url of the page is changed.
    It is responsible for using the url to call the appropriate python 
    function to update the main contents of the page.
    These contents will be placed inside of the div with the id of "main-content".
    """
    if pathname == "/":
        return image_upload()
    elif pathname == "/test":
        return "success"
    elif pathname == "/segment":
        return manual_segmentation_page()
    return html.Div([
        html.Div("Invalid url"),
        html.H3('You are on page {}'.format(pathname))
    ])


if __name__ == '__main__':
    app.run_server(debug=True)

