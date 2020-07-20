import dash
import dash_core_components as dcc
import dash_html_components as html

"""
This is the navbar that displays at the top of every page.
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
    upload_component_style = {
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        }

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
                                                            style=upload_component_style,
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
                                                            style=upload_component_style,
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

# This does not render anything but is necessary for routing to function
def url_bar():
    return dcc.Location(id='url', refresh=False)


def header():
    return html.Div(
        children=[
            url_bar(),
            nav_bar(),
        ],
        id="header",
    )


def manual_segmentation_page():
    pass
