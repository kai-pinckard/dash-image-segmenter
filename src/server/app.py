import dash
import dash_core_components as dcc
import dash_html_components as html
from urllib.parse import quote as urlquote
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from components import *
import os
import base64
from flask import Flask, send_from_directory
import imageio


import tasks

"""
This is a list storing all the promises from the work queue
"""
results = []

"""
cctools work queue
"""
#import work_queue as wq

# create a new queue listening on port 9123
#q = wq.WorkQueue(9123)
"""
See segment dependencies these can be removed if all segmentation
is performed in other processes. Note that the see module must be added to
the python path manually. One good way to do this is described here:
https://medium.com/@arnaud.bertrand/modifying-python-s-search-path-with-pth-files-2a41a4143574

When see segment has been packaged and can be pip installed this will no longer be necessary.
"""
#from see import GeneticSearch, Segmentors
"""
Install instructions conda

conda create
conda activates envs
conda install -c conda-forge dash-renderer
conda install -c conda-forge dash 
conda install pandas
conda install -y -c conda-forge ndcctools


Find an up to date version here:
http://ccl.cse.nd.edu/software/download
Download here:
http://ccl.cse.nd.edu/software/files/cctools-7.1.6-source.tar.gz

Command line Download:
wget -O cctools-7.1.6-source.tar.gz http://ccl.cse.nd.edu/software/files/cctools-7.1.6-source.tar.gz

Install from source ndcctools
tar zxf cctools-*-source.tar.gz
cd cctools-*-source
./configure
make
# by default, CCTools is installed at ~/cctools. See below to change this default.
make install
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

"""
Note: header is not really updated it's just that dash requires
every callback to have an output
"""
@app.callback(
    Output("header", "n_clicks"),
    [Input('segmentation-button', 'n_clicks')]
)
def start_segmentation(num_clicks):
    print(num_clicks)
    if num_clicks == None:
        return 0
    else:
        #return tasks.simple_test_task.delay(2,34)
        print("called")
        images = uploaded_files()
        img = images[0]
        gmask = images[1]
        
        print(img)
        print(gmask)
        img = imageio.imread(os.path.join(UPLOAD_DIRECTORY, img))
        gmask = imageio.imread(os.path.join(UPLOAD_DIRECTORY, gmask))
        #img = get_image_encoding(img)
        print(img)
        #gmask = get_image_encoding(gmask)
        print("here")
        result = tasks.segment.delay(img, gmask, 5, 10)
        print("here2")
        results.append(result)
        print("here3")
        print(results[0].get())
        return 0


"""

"""
def get_image_encoding(image_path):
    with open(os.path.join(UPLOAD_DIRECTORY, image_path), "rb") as imageFile:
        encoded_img = base64.b64encode(imageFile.read())
        json_serializable_img = encoded_img.decode("utf-8")
    return json_serializable_img

     
                

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
def download(file_name):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, file_name, as_attachment=True)

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
        return see_segment()
    return html.Div([
        html.Div("Invalid url"),
        html.H3('You are on page {}'.format(pathname))
    ])


if __name__ == '__main__':
    app.run_server(debug=True, port=8888)

