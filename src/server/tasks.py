from celery import Celery
from see import GeneticSearch, Segmentors
import base64
import imageio
from PIL import Image
import requests
import os

"""To Run a worker: celery -A tasks worker --loglevel=info """

from celery.utils.log import get_task_logger

DASH_URL = "http://127.0.0.1:8888"
WORKER_IMAGE_FOLDER = os.path.join(os.getcwd(), "worker_images")

if not os.path.isdir(WORKER_IMAGE_FOLDER):
    os.mkdir(WORKER_IMAGE_FOLDER)

logger = get_task_logger(__name__)

client = Celery('tasks', backend='rpc://', broker='amqp://guest@localhost//')

client.conf.task_serializer = 'pickle'
client.conf.result_serializer = 'json'
client.conf.accept_content = ['pickle', 'json']

def get_path(worker_image_file_name):
    """
    returns the absolute path to a worker image file given
    its filename.
    """
    return os.path.join(WORKER_IMAGE_FOLDER, worker_image_file_name)

def download_and_store_image(image_name):
    """
    Do not use this function with get_path, just use the image 
    file name
    """
    response = requests.get(DASH_URL + "/download/" + image_name)
    with open(get_path(image_name), "wb") as image_file:
        image_file.write(response.content)

def upload_file_to_dash(file_name):
    """
    Use this function if you have only a file name.
    """
    url = DASH_URL + "/files/" + file_name
    files = {'image': open(get_path(file_name), 'rb')}
    requests.post(url, files=files)

@client.task
def evaluate_segmentation(segmenter, image):
    download_and_store_image(image)

    image = imageio.imread(get_path(image))
    mask = segmenter.evaluate(image)
    imageio.imwrite(get_path("mask.jpg"), mask)
    upload_file_to_dash("mask.jpg")
    return "mask.jpg"

@client.task
def conduct_genetic_search(img, gmask, num_gen, pop_size):
    """
    Note: this task could be sped up by
    rewriting it to send the evaluation and fitness function
    calls to other workers as tasks.
    """

    # Only needed on some images
    # Convert the RGB 3-channel image into a 1-channel image
    # gmask = (np.sum(gmask, axis=2) > 0)

    download_and_store_image(img)
    download_and_store_image(gmask)

    img = imageio.imread(get_path(img))
    gmask = imageio.imread(get_path(gmask))

    my_evolver = GeneticSearch.Evolver(img, gmask, pop_size=pop_size)
    
    # Conduct the genetic search
    population = None

    for _ in range(num_gen):

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

    return data