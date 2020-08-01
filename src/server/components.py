import dash
import dash_core_components as dcc
import dash_html_components as html

def nav_bar():
    """
    This is the navbar that displays at the top of every page.
    """
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
                                               href="/",
                                               )
                                    ],
                                    className="nav-item",
                                ),
                                html.Li(
                                    children=[
                                        html.A("Results",
                                               className="nav-link",
                                               href="seesegment",
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

def url_bar():
    """
    This does not render anything but is necessary for routing to function
    """
    return dcc.Location(id='url', refresh=False)

def header(update_interval_in_seconds=5):
    """
    This header should always and by default is always included in every
    page.
    """
    return html.Div(
        children=[
            url_bar(),
            nav_bar(),
            dcc.Interval(
            id='interval-component',
            interval=update_interval_in_seconds*1000, # in milliseconds
            n_intervals=0
        )
        ],
        id="header",
    )

def empty_col():
    """
    Used to create empty columns to allow bootstrap to properly align other
    columns.
    """
    return html.Div(className="col")

def upload():
    """
    Wraps the contents of the upload page in some divs so that it appears
    centered on the page.
    """
    return html.Div(
        children=[
            empty_col(),
            html.Div(
                children=[
                    upload_component()
                ],
                className="col"
            ),
            empty_col(),
        ],
        className="row mt-5"
    )

def upload_component():
    """
    The actual contents of the upload page.
    """
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
            html.H2(
                "Uploaded Files:",
                className="mt-4"
            ),
            html.Ul(id="file-list"),
            html.A(
                html.Button(
                    "Continue",
                    className="btn btn-success mt-4 text-center",
                ),
                href="seesegment",
                className="text-center",
            ),
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
                        style={'height': '300px'},
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
    using the see segment workers. This page is intended primarily as a development tool
    and does not support any manual segmentation.

    If the images are not updating to reflect changes in the code try refreshing
    the page and/or clearing your browser cache.
    """
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(className="col-1"),
                    image_display_column(
                        "/static/Chameleon.jpg", "RGB Image", "Image not found", "rgb_image"),
                    image_display_column(
                        "/static/mask.jpg", "Current Best", "Image not found", "mask_image"),
                    image_display_column(
                        "/static/Chameleon_GT.jpg", "Ground Truth", "Image not found", "label_image"),

                    html.Div(className="col-1"),
                ],
                className="row mt-5",
                id="image-sidebyside",
            ),
            html.Div(
                children=[
                    html.Div(className="col"),
                    html.Div(children=[
                        html.A(
                            html.Button(
                                "Back",
                                className="btn btn-success mr-1",
                            ),
                            href="/",
                        ),
                        html.Button(
                            "Begin Segmentation",
                            className="btn btn-success",
                            id="segmentation-button"
                            ),
                    ],
                        className="col text-center"),
                    html.Div(className="col")
                ],
                className="row mt-2"
            ),
            display_segmentation_code(
                segmentation_code, fitness, segmentation_parameters)
        ],
        id="see-segment-content"
    )

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
                    html.H2("Fitness: " + str(formatted_fitness(fitness))),
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(
                                        className="progress-bar bg-success",
                                        role="progressbar",
                                        style={
                                            "width": str(fitness_to_progress(fitness))+"%"},
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
    and eventually will allow them to select which images to use
    when multiple images have been uploaded.
    """
    pass

def manual_segmentation_page():
    """
    Add the manual segmentation code here.
    """
    return "To Be Implemented."
