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
    print(image_name)
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

