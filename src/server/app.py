import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# external JavaScript files may not be necessary
external_scripts = [
    "https://code.jquery.com/jquery-3.3.1.slim.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js",
]


# external CSS stylesheets
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

"""
This is the navbar that displays at the top of the page.
"""
def nav_bar():
    return (
        html.Nav(
        children=[
            html.A(
                "See Segment",
                className="navbar-brand",
                href="#",
            ),
        html.Div(
            children=[
                html.Ul(
                    children=[
                        html.Li(
                            children=[
                                html.A("Upload Files",
                                className="nav-link",
                                href="index",
                                )
                            ],
                            className="nav-item",
                        ),
                        html.Li(
                            children=[
                                html.A("Results",
                                className="nav-link",
                                href="monitor",
                                )
                            ],
                            className="nav-item",
                        )
                    ],
                    className="navbar-nav ml-auto"
                )
            ],
            className="collapse navbar-collapse",
        )
        ],
        className="navbar navbar-expand-lg navbar-dark bg-primary"
        )
    )

def image_upload():
    return (
        html.Div(
            children=[
                html.Div(
                    children="",
                    className="col",
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Form(
                                            children=[
                                                html.Div(
                                                    children=[
                                                        html.Label(
                                                            children="Select an RGB image to learn segmentations on.",
                                                            htmlFor="rgb_image",
                                                        ),
                                                        dcc.Upload(
                                                            children=[
                                                                html.A("Select a file.")
                                                            ],
                                                            style={
                                                                'width': '100%',
                                                                'height': '60px',
                                                                'lineHeight': '60px',
                                                                'borderWidth': '1px',
                                                                'borderStyle': 'dashed',
                                                                'borderRadius': '5px',
                                                                'textAlign': 'center',
                                                            },
                                                            className="form-control-file",
                                                            id="exampleFormControlFile1",
                                                        )
                                                    ],
                                                    className="form-group m-3",
                                                ),
                                                html.Div(
                                                    children=[
                                                        html.Label(
                                                            children="Select a ground truth segmentation label image to use.",
                                                            htmlFor="label_image",
                                                        ),
                                                        dcc.Upload(
                                                            children=[
                                                                html.A("Select a file.")
                                                            ],
                                                            style={
                                                                'width': '100%',
                                                                'height': '60px',
                                                                'lineHeight': '60px',
                                                                'borderWidth': '1px',
                                                                'borderStyle': 'dashed',
                                                                'borderRadius': '5px',
                                                                'textAlign': 'center',
                                                            },
                                                            className="form-control-file",
                                                            id="exampleFormControlFile2",
                                                        )
                                                    ],
                                                    className="form-group m-3",
                                                ),
                                                html.Div(
                                                    children=[
                                                        html.Button(
                                                            children="Upload Images",
                                                            type="submit",
                                                            className="btn btn-primary"
                                                        ),
                                                    ],
                                                    className="form-group m-3",

                                                )
                                            ],
                                            action="verify",
                                            method="post",
                                            encType="multipart/form-data",
                                        )
                                    ],
                                    className="card border rounded border-success",
                                )
                            ],
                        )
                    ],
                    className="col-sm-8 col-lg-4 col-md-6 m-5",
                ),
                html.Div(
                    children="",
                    className="col",
                ),
        ],
        className="row mt-5"
        )
    )



"""
To add new components easily write a function that returns the component and then call that function
inside of the children property below.
"""
app.layout = html.Div(
    children=[
        nav_bar(),
        image_upload(),
    ],
    className="container-fluid",
    )


if __name__ == "__main__":
    app.run_server(debug=True)