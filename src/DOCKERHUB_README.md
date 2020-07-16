# For see-segment maintainers only:
## To upload a Docker image to Docker Hub:
sudo docker login -u seesegment --password-stdin REQUEST_THE_PASSWORD

## Updating the Docker images:
When updating docker images make sure to modify the yaml files to use the latest verion of the container

After making and testing any code changes locally, when want to update the containers on dockerhub

### Build and push updated see-segment image:
Run inside the see-segment directory
Replace the :0.0.4 with the version number you are creating
Also be sure to update the version number in the yaml files.

`sudo docker build -t seesegment/seesegment:0.0.4 .`

`sudo docker push seesegment/seesegment:0.0.4`

### Build and push updated server image:
Run inside the seesegment/see_server directory
Replace the :0.0.4 with the version number you are creating
Also be sure to update the version number in the yaml files.

`sudo docker build -t seesegment/seeserver:0.0.4 .`

`sudo docker push seesegment/seeserver:0.0.4`


### To run the server locally in a container
`sudo docker run --name <Replace with Name> -p 8080:8080 <Replace with image>`

### Useful commands
The following are useful docker commands explained by the tldr command
(https://tldr.sh/)

#### List currently running docker containers:
`docker ps`

#### List all docker containers (running and stopped):
`docker ps -a`

#### Start a container from an image, with a custom name:
`docker run --name {{container_name}} {{image}}`

#### Start or stop an existing container:
`docker {{start|stop}} {{container_name}}`

#### Pull an image from a docker registry:
`docker pull {{image}}`

#### Open a shell inside of an already running container:
`docker exec -it {{container_name}} {{sh}}`

#### Remove a stopped container:
`docker rm {{container_name}}`

#### Fetch and follow the logs of a container:
`docker logs -f {{container_name}}`

