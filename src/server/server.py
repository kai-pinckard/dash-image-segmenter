import cherrypy
import json
import os
import imageio
from see import GeneticSearch, Segmentors

"""
uploaded_file must match the name field of the input element
in the relevant html file. 

save_as is the desired file name for the uploaded file to be
stored as.
"""
def save_uploaded_file(uploaded_file, save_as):
    saved_file_path = os.path.join(os.getcwd(), save_as)
    size = 0
    with open(saved_file_path, "wb") as f:
        while True:
            # Read the image data in chunks of 8192
            data = uploaded_file.file.read(8192)
            if not data:
                break
            # Write the current chunk into the file to save on disk
            f.write(data)
            size += len(data)
"""
Populates html files with dynamic data passed through the data
parameter. This function returns html that is ready to render.
html_path: the path to the html file to fill
data: a list containing args for string formatting

Note: In the html files being filled there are '{}'s with a number
inside them. For example {0} will be the place where the text in 
index 0 of the data array will be inserted into the html template.
"""
def fill_html_template(html_path, data):
    with open(html_path, "r") as f:
        html = f.read()
    # the * converts the list into args
    return html.format(*data)
            

class Root:

    def __init__(self):
        self.best_fit = -1
        self.best_ind = {}
        self.base_dir = os.getcwd()
        self.web_pages_dir = os.path.join(self.base_dir, "web_pages")
        """
        The images must be stored in the directory public
        so that they can be displayed to the user.
        """
        self.static_dir = os.path.join(self.base_dir, "public")

        # Remove any image files previously saved while the server was running
        images = os.listdir(self.static_dir)
        for image in images:
            img_path = os.path.join(self.static_dir, image)
            os.remove(img_path)
        """
        The images must be stored in the directory public
        so that they can be displayed to the user.

        Note: if the filenames are changed then they must also be updated
        in segment_container.py
        """
        self.rgb_filename = os.path.join("public", "rgb.jpg")
        self.label_filename = os.path.join("public", "label.jpg")

    # Methods with expose are accessible urls in browser
    @cherrypy.expose
    def index(self):
        html_path = os.path.join(os.getcwd(), "web_pages", "index.html")
        return open(html_path)

    # Users are redirected to this page after submiting their files.
    @cherrypy.expose
    def verify(self, rgb_image, label_image):
        save_uploaded_file(rgb_image, self.rgb_filename)
        save_uploaded_file(label_image, self.label_filename)

        html_path = os.path.join(os.getcwd(), "web_pages", "verify.html")
        return open(html_path)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def update(self):
        result = {"operation": "request", "result": "success"}

        input_json = cherrypy.request.json
        input_json = json.loads(input_json)

        if self.best_fit == -1 or self.best_ind["fitness"] > input_json["fitness"]:
            self.best_ind = input_json
            self.best_fit = self.best_ind["fitness"]
        return result

    @cherrypy.expose
    def monitor(self):
        html_path = os.path.join(os.getcwd(), "web_pages", "monitor.html")
        
        if self.best_fit != -1:
            # If there is a segmentor then display the images segmentation
            img = imageio.imread(self.rgb_filename)
            gmask = imageio.imread(self.label_filename)

            print(self.best_ind["params"])
            self.best_ind["params"]
            seg = Segmentors.algoFromParams(self.best_ind["params"])
            mask = seg.evaluate(img)

            static_dir = os.path.join(os.getcwd(), "public")
            imageio.imwrite(os.path.join(static_dir, "mask.jpg"), mask)

            code = GeneticSearch.print_best_algorithm_code(self.best_ind["params"])

            # Calculate progress bar precentage
            percentage = (1 - self.best_ind["fitness"]) * 100
            
            rounded_fitness = float("{0:.2f}".format(self.best_ind["fitness"]))

            data = ["", code, self.best_ind["params"], rounded_fitness, percentage]
        else:
            data = ['style="display:none;"', "", "", "",""]

        return fill_html_template(html_path, data)


if __name__ == "__main__":

    conf = {
        'global': {
            'server.socket_host':'0.0.0.0',
            'server.socket_port': 8080,
            'tools.caching.on': False,
            'tools.caching.debug': False
            },

        # This mounts the public directory onto the security directory
        # Anything inside the public directory will appear as if it is in
        # the static directory to the server. 
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.getcwd(), "public"),
            'tools.expires.on': True, # cached browser data expires
            'tools.expires.secs': 1 # cached data expires after 1 sec old
            }
        }
    cherrypy.quickstart(Root(), '/', conf)