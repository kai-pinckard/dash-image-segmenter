from celery import Celery
from see import GeneticSearch, Segmentors
import base64
import imageio


""" celery -A tasks worker --loglevel=info """

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

client = Celery('tasks', backend='rpc://', broker='amqp://guest@localhost//')

client.conf.task_serializer = 'pickle'
client.conf.result_serializer = 'pickle'
client.conf.accept_content = ['pickle']

def store_encoded_image(encoded_image, file_name):
    with open(file_name, "wb") as imageFile:
        imageFile.write(encoded_image.decode("base64"))

def store_and_load_encoded_image(encoded_image, file_name):
    store_encoded_image(encoded_image, file_name)
    python_image_object = imageio.imread(file_name)
    return python_image_object

@client.task
def segment(img, gmask, num_gen, pop_size):

    # Only needed on some images
    # Convert the RGB 3-channel image into a 1-channel image
    # gmask = (np.sum(gmask, axis=2) > 0)

    
    logger.info("ran")
    print("heres")
    #img = store_and_load_encoded_image(img, "rgb.png")
    #gmask = store_and_load_encoded_image(gmask, "label.png")
    # Create an evolver
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

        return data

@client.task
def simple_test_task(num1, num2):
    print("ran")
    return num1 + num2