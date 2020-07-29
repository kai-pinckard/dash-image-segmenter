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
                                                    className="form-group m-",

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

def dataset_upload():
    return html.Div(
    [
        html.H2("Upload"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and drop or click to select a file to upload."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.H2("File List"),
        html.Ul(id="file-list"),
    ],
    style={"max-width": "500px"},
)

def image_display_column(image_source, image_label, alt_text, image_id=""):
    """
    This is a reusable component for displaying an image with a label.
    """
    return html.Div(
        children=[
            html.H2(image_label),
            html.Div(
                children=[
                    html.Img(
                        src=image_source,
                        alt=alt_text,
                        id=image_id,
                        # TODO Find a better way of controlling the image height.
                        style={'height':'300px'},
                        className="image-fluid",
                    ),
                ],
            className="card border rounded border-success",
            ),
        ],
        className="col-sm-3 col-lg-3 col-md-3 m-4 text-center h-25",
    )

def see_segment(segmentation_code, fitness, segmentation_parameters):
    """
    This page displays the current segmentation progress of an image
    using the seesegment workers. This page is intended primarily as a development tool
    and does not support any manual segmentation.
    """
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(className="col-1"),

                    image_display_column("/static/Chameleon.jpg", "RGB Image", "Image not found", "rgb_image"),
                    image_display_column("/static/mask.jpg", "Current Best", "Image not found", "mask_image"),
                    image_display_column("/static/Chameleon_GT.png", "Ground Truth", "Image not found", "label_image"),
                
                    html.Div(className="col-1"),
                ],
                className="row mt-5",
                id="image-sidebyside"
            ),
            html.Div(
                children=[
                    html.Div(className="col"),
                    html.Div(children=[
                        html.Button("Begin Segmentation",
                            className="btn btn-success",
                            id="segmentation-button")
                    ],
                    className="col text-center"),
                    html.Div(className="col")
                ],
                className="row mt-2"
            ),
            display_segmentation_code(segmentation_code, fitness, segmentation_parameters)
        ],
        id="see-segment-content"
    )

def empty_col():
    return html.Div(className="col")



def display_segmentation_code(segmentation_code="Please wait.", fitness=1.0, segmentation_parameters="Please wait."):

    def formatted_fitness(fitness):
        return float("{0:.2f}".format(fitness))

    def fitness_to_progress(fitness):
        # Calculate progress bar precentage
        return (1 - fitness) * 100

    return html.Div(
        children=[
            empty_col(),
            html.Div(
                children=[
                    html.H2("Segmentation Code:"),
                    html.Div(
                        children=[
                            html.Pre(
                                children=[
                                    html.Code(segmentation_code)
                                ]
                            )
                        ],
                        className="card border rounded",
                    )
            ],
            className="col-sm-8 col-md-6 col-lg-4",
            ),
            html.Div(
                children=[
                    html.H2("Fitness: " + str(formatted_fitness(fitness)) ),
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(
                                        className="progress-bar bg-success",
                                        role="progressbar",
                                        style=("width: "+str(fitness_to_progress(fitness))),
                                        ),
                                ],
                                className="progress",
                            )
                        ],
                        className="card border rounded",
                    ),
                    html.H2("Parameters:",
                    className="mt-4"
                    ),
                    html.Div(
                    children=[
                        html.P(segmentation_parameters)
                    ],
                    className="card border rounded",
                )
            ],
            className="col-sm-8 col-md-6 col-lg-4",
            ),
            empty_col(),
        ],
        className="row mt-5"
    )



def verify_images():
    """
    This page allows the user to view the images that they have uploaded
    and eventually will allow them to select which images to use when multiple images have been uploaded.
    """
    pass

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

"""
Add the manual segmentation code here.
"""
def manual_segmentation_page():
    pass
