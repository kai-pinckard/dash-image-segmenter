import dash
import dash_core_components as dcc
import dash_html_components as html
from urllib.parse import quote as urlquote
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from components import *
import os
import base64
from flask import Flask, send_from_directory, request, abort
import imageio
from see import Segmentors, GeneticSearch

import tasks

"""
This is a list storing all the promises from the work queue
"""
results = []

"""
See segment dependencies these can be removed if all segmentation
is performed in other processes. Note that the see module must be added to
the python path manually. One good way to do this is described here:
https://medium.com/@arnaud.bertrand/modifying-python-s-search-path-with-pth-files-2a41a4143574

When see segment has been packaged and can be pip installed this will no longer be necessary.
"""

UPLOAD_DIRECTORY = os.path.join(os.getcwd(), "uploads")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

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

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(server=server,
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


@app.callback(
    Output("mask_image", "src"),
    [Input("interval-component", "n_intervals")],
    [State("mask_image", "src")]
)
def periodic_update(n_intevals, source):
    if len(results) > 0:
        images = uploaded_files()
        img = images[0]
        #image = imageio.imread(os.path.join(UPLOAD_DIRECTORY, img))
        print("testing")
        print("test", results[0].state)
        if results[0].ready():
            print("ren")
            segmenter = Segmentors.algoFromParams((results[0].get())["params"])
            mask_image = tasks.evaluate_segmentation.delay(segmenter, img).get()
            imageio.imwrite("mask.png", mask_image)
            print("image written")
            return source
        print("not ready")
        print(results[0].ready())
    return source



def submit_segmentation_task(image, label):
    """
    Given an image and a label which can either both be filenames of
    images inside the UPLOAD_DIRECTORY or both can be imageio objects
    this function will add a celery task to run seesegment on the image and the
    label
    """
    """ if isinstance(image, str) and isinstance(label, str):
        img = imageio.imread(os.path.join(UPLOAD_DIRECTORY, image))
        gmask = imageio.imread(os.path.join(UPLOAD_DIRECTORY, label)) """
    result = tasks.conduct_genetic_search.delay(image, label, 1, 2)
    results.append(result)


"""
Note: header is not really updated it's just that dash requires
every callback to have an output
"""
@app.callback(
    Output("see-segment-content", "children"),
    [Input('segmentation-button', 'n_clicks')],
    [State("see-segment-content", "children")]
)
def start_segmentation(num_clicks, children):
    print(num_clicks)
    if num_clicks == None:
        return children
    else:
        images = uploaded_files()
        img = images[0]
        gmask = images[1]
        print("img", img, "gmask", gmask)
        submit_segmentation_task(img, gmask)

        return children

def get_image_encoding(image_path):
    with open(os.path.join(UPLOAD_DIRECTORY, image_path), "rb") as image_file:
        encoded_img = base64.b64encode(image_file.read())
        json_serializable_img = encoded_img.decode("utf-8")
    return json_serializable_img

@server.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""

    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories directories allowed")

    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)

    # Return 201 CREATED
    return "", 201

@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]

def save_file(name, content):
    """Decode and store an uploaded file, writing to disk."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))



@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

# This function may be insecure
@server.route("/static/<image_name>")
def serve_image(image_name):
    return send_from_directory(UPLOAD_DIRECTORY, image_name)

def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files



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
    elif pathname == "/dataset":
        return dataset_upload()
    elif pathname == "/segment":
        return manual_segmentation_page()
    elif pathname == "/seesegment":
        return see_segment("code", 0.5, "test parsmas")
    return html.Div([
        html.Div("Invalid url"),
        html.H3('You are on page {}'.format(pathname))
    ])


if __name__ == '__main__':
    app.run_server(debug=True, port=8888)

