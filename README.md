# Why Use Image Segmenter Finder:
Image segmentation is a common step in many scientific workflows. However, it remains a time consuming and often expensive part of the research process.
To address this problem, this project utilizes the see-segment tool, which finds algorithm(s) to automatically segment images.This project provides a web interface for performing image segmentation and uses genetic algorithms to learn which image segmentation algorithms and parameters will provide a good segmentation for the types of images that are uploaded. The project can be run either locally or in any cloud environment that supports kubernetes. Running locally is a great way to test out the repository and see if it fits your needs.

However, the algorithm search space explored by see-segment is extremely large and often requires a large amount of computation. To speed up the search process many copies of the see-segment search algorithm should be run in parallel to quickly obtain good results. Unfortunately installing and running see-segment at scale is difficult, as computational environments can differ in the tools and packages that are available. 

This project encapsulates the see-segment tool into Docker containers which allow them to easily be run anywhere Docker containers are supported (ex AWS, Google Cloud, AZUR, etc). Furthermore, Kubernetes is used to manage the multiple instances of the containers to make running at scale on preemptible machines easy. Hundreds of these containers can work together and communicate with a lead container running an easy to use web interface that allows scientists to upload images in the same manner they would on any other website. The current best segmentation algorithm is then displayed to the user’s web browser in real time as the see-segment containers run in the background.

# How to Use Image Segmenter Finder Locally:
## How To Install Image Segmenter Finder Locally:

### Clone this repository:

`git clone https://github.com/kai-pinckard/dash-image-segmenter`

### Change into the project directory/folder:

`cd dash-image-segmenter`

### Create a virtual environment for the project:

`python -m venv env`

### Activate the virtual environment:


`source env/bin/activate`

### Install the projects dependencies:

`pip install -r requirements.txt`

### Install RabbitMQ:
`sudo apt-get install rabbitmq-server`

## How to Run Image Segmenter Finder Locally:
Make sure that your working directory is the server folder inside the dash-image-segmenter folder. Then run:

`python app.py`

Run the following command in as many terminals tabs as you want to have workers.


`celery -A tasks worker --loglevel=info`



