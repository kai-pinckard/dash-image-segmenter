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
from PIL import Image
from see import Segmentors, GeneticSearch


import tasks

import sys, getopt

"""
Suggested improvements:

Add a web page/mechanism for selecting which of all the images that have been
uploaded should be used in the segmentation process.

Add a better way of managing promises from the work queue than the results list.

Add a better way of managing individuals and their fitnesses.

Rewrite the task conduct genetic search to create subtasks where the subtasks 
calculate the segmentations and the fitnesses. 

Add multiimage fitness function and task.
"""

#=====================================================================
# Handle command line arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "l:")
except getopt.GetoptError:
    print("For help run:")
    print("python app.py -h")
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        print("flags:")
        print("l: Location")
        print("To run in a kubernetes cluster run:")
        print("python app.py -l cluster")
        print("To run locally run:")
        print("python app.py")
        sys.exit()
    elif opt == "-l":
        if arg == "cluster":
            tasks.DASH_URL = "http://serverservice"
print("Running with parameters:")
print("DASH_URL =", tasks.DASH_URL)
print("")
#=====================================================================

"""
This is a list storing all the promises from the work queue
"""
results = []

"""
These stores the current best fitness and individual.
"""
best_fit = -1
best_ind = {}

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

""" 
Normally, Dash creates its own Flask server internally. By creating our own,
we can create a routes for interacting with files directly.
"""
server = Flask(__name__)
app = dash.Dash(server=server,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
                ],
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div(
    children=[
        header(update_interval_in_seconds=10),
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
def periodic_update(n_intevals, src):
    if update_best_individual():
        img = "Chameleon.jpg"
        segmenter = Segmentors.algoFromParams((results[0].get())["params"])
        return "/static/" + tasks.evaluate_segmentation.delay(segmenter, img).get()
    return src


def update_best_individual():
    """
    this function checks all the promises in the global results variable
    every promise that is ready is then checked to see if it contains 
    """
    update_occured = False
    global best_fit
    global best_ind
    # Note results accumulate in results so it will take longer and longer to search
    for result in results:
        if result.ready():
            data = result.get()
            # since a lower fitness value is better
            if best_fit == -1 or best_ind["fitness"] > data["fitness"]:
                best_ind = data
                best_fit = best_ind["fitness"]
                update_occured = True
    return update_occured

def has_results():
    """
    This function returns true if any genetic searches have returned results.
    """
    return best_fit != -1

@app.callback(
    Output("best-segmentation-code", "children"),
    [Input("interval-component", "n_intervals")],
    [State("best-segmentation-code", "children")]
)
def update_code_display(n_intevals, currently_displayed_code):
    if has_results():
        return GeneticSearch.print_best_algorithm_code(best_ind["params"])
    else:
        return currently_displayed_code


@app.callback(
    Output("best-segmentation-params", "children"),
    [Input("interval-component", "n_intervals")],
    [State("best-segmentation-params", "children")]
)
def update_params_display(n_intevals, currently_displayed_params):
    if has_results():
        return str(best_ind["params"])
    else:
        return currently_displayed_params


def formatted_fitness(fitness):
    return float("{0:.2f}".format(fitness))

def fitness_to_progress(fitness):
    # Calculate progress bar precentage
    return (1 - fitness) * 100

@app.callback(
    Output("best-segmentation-fitness", "children"),
    [Input("interval-component", "n_intervals")],
    [State("best-segmentation-fitness", "children")]
)
def update_fitness_display(n_intevals, currently_displayed_fitness):
    
    if has_results():
        return "Fitness: " + str(formatted_fitness(best_ind["fitness"]))
    else:
        return currently_displayed_fitness

@app.callback(
    Output("best-segmentation-fitness-bar", "style"),
    [Input("interval-component", "n_intervals")],
    [State("best-segmentation-fitness-bar", "style")]
)
def update_fitness_bar(n_intevals, currently_displayed_fitness):
    
    if has_results():
        return {"width": str(fitness_to_progress(best_ind["fitness"]))+"%"}
    else:
        return currently_displayed_fitness


def get_best_segmentation_info():
    return ""

def submit_segmentation_task(image, label):
    """
    Given the filenames of the image and the label this 
    function will add a conduct_genetic_search function call to the work queue
    """
    result = tasks.conduct_genetic_search.delay(image, label, 1, 2)
    results.append(result)

@app.callback(
    Output("see-segment-content", "children"),
    [Input('segmentation-button', 'n_clicks')],
    [State("see-segment-content", "children")]
)
def start_segmentation(num_clicks, children):
    """
    Note: By returning children nothing is actually being updated this just
    allows a task to be run at on a button press
    """
    if num_clicks == None:
        return children
    else:
        img = "Chameleon.jpg"
        gmask = "Chameleon_GT.jpg"
        print("img", img, "gmask", gmask)
        submit_segmentation_task(img, gmask)
        return children

@server.route("/files/<filename>", methods=["POST"])
def post_image(filename):
    """
    Upload an image with an http request. This is used by the worker to
    send images back to the server.
    """

    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories directories allowed")

    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    data = request.files["image"].read()
    with open(file_path, "wb") as fp:
        fp.write(data)

    image = Image.open(file_path)
    os.remove(file_path)

    # Convert png images into jpg images
    if file_path.endswith(".png"):
        rgb_image = image.convert("RGB")
        file_path = file_path.replace("png", "jpg")
        rgb_image.save(file_path)
    else:
        image.save(file_path)

    print("posted image saved", file_path)

    # Return 201 CREATED
    return "", 201

@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_file_list(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_image(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]

def save_image(name, content):
    """
    Save images and convert images that are uploaded on the web page
    all png images will be saved as jpg images.
    """
    data = content.encode("utf8").split(b";base64,")[1]
    file_name = os.path.join(UPLOAD_DIRECTORY, name)
    with open(file_name, "wb") as fp:
        fp.write(base64.decodebytes(data))

    # Note writing the binary to a file and then reading it and resaving it
    # is inefficient consider improving this.

    image = Image.open(file_name)
    os.remove(file_name)

    # Convert png images into jpg images
    if file_name.endswith(".png"):
        rgb_image = image.convert("RGB")
        file_name = file_name.replace("png", "jpg")
        rgb_image.save(file_name)
    else:
        image.save(file_name)
    
@server.route("/download/<path:path>")
def download(path):
    """
    Serve a file from the upload directory to enable downloads
    """
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True, cache_timeout=0)

@server.route("/static/<image_name>")
def serve_image(image_name):
    """
    This function serves images so that they can be displayed on pages
    on the dash web app.
    """
    return send_from_directory(UPLOAD_DIRECTORY, image_name, cache_timeout=0)

def file_download_link(filename):
    """
    Create a Dash link element that downloads a file from the app
    """
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


def uploaded_files():
    """
    List the files stored in the upload directory
    """
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
        return upload()
    elif pathname == "/upload":
        return upload()
    elif pathname == "/segment":
        return manual_segmentation_page()
    elif pathname == "/seesegment":
        return see_segment("Start a segmentation job.", 1.0, "Start a segmentation job.")
    return html.Div([
        html.Div("Invalid url"),
        html.H3('You are on page {}'.format(pathname))
    ])

if __name__ == '__main__':
    app.run_server(debug=True, port=8888)

