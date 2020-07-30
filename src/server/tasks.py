from celery import Celery
from see import GeneticSearch, Segmentors
import base64
import imageio
import requests

"""To Run a worker: celery -A tasks worker --loglevel=info """

from celery.utils.log import get_task_logger


DASH_URL = "http://127.0.0.1:8888"

logger = get_task_logger(__name__)

client = Celery('tasks', backend='rpc://', broker='amqp://guest@localhost//')

client.conf.task_serializer = 'pickle'
client.conf.result_serializer = 'json'
client.conf.accept_content = ['pickle', 'json']

def store_encoded_image(encoded_image, file_name):
    with open(file_name, "wb") as imageFile:
        imageFile.write(encoded_image.decode("base64"))

def store_and_load_encoded_image(encoded_image, file_name):
    store_encoded_image(encoded_image, file_name)
    python_image_object = imageio.imread(file_name)
    return python_image_object

def download_and_store_image(image_name):
    response = requests.get(DASH_URL + "/download/" + image_name)
    with open(image_name, "wb") as image_file:
        image_file.write(response.content)

def upload_file_to_dash(file_name):
    url = DASH_URL + "/files/" + file_name
    files = {'media': open(file_name, 'rb')}
    requests.post(url, files=files)

@client.task
def evaluate_segmentation(segmenter, image):
    download_and_store_image(image)
    image = imageio.imread(image)
    mask = segmenter.evaluate(image)
    imageio.imwrite("mask.png", mask)
    upload_file_to_dash("mask.png")
    return "mask.png"

@client.task
def conduct_genetic_search(img, gmask, num_gen, pop_size):
    """
    Note: this task could be sped up substantially by
    rewriting it to send the evaluation and fitness function
    function calls to other works as tasks.
    """
    # Only needed on some images
    # Convert the RGB 3-channel image into a 1-channel image
    # gmask = (np.sum(gmask, axis=2) > 0)

    #img = store_and_load_encoded_image(img, "rgb.png")
    #gmask = store_and_load_encoded_image(gmask, "label.png")
    # Create an evolver

    print("ran") 
    download_and_store_image(img)
    download_and_store_image(gmask)

    img = imageio.imread(img)
    gmask = imageio.imread(gmask)

    my_evolver = GeneticSearch.Evolver(img, gmask, pop_size=pop_size)
    
    # Conduct the genetic search
    population = None

    for i in range(num_gen):

        # if population is uninitialized
        if population is None:
            population = my_evolver.run(ngen=1)
        else:
            # Simulate a generation and store population in population variable
            population = my_evolver.run(ngen=1, population=population)

        # Take the best segmentor from the hof and use it to segment the rgb image
        seg = Segmentors.algoFromParams(my_evolver.hof[0])
        mask = seg.evaluate(img)

        # Calculate and print the fitness value of the segmentor
        fitness = Segmentors.FitnessFunction(mask, gmask)[0]
        params = my_evolver.hof[0]

        # Combine data into a single object
        data = {}
        data["fitness"] = fitness
        data["params"] = params
        #data["segmenter"] = seg

        return data

@client.task
def simple_test_task(num1, num2):
    print("ran")
    return num1 + num2