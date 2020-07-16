From python:3.8.3

RUN apt-get update && apt-get install -y git
RUN pip install cherrypy numpy scikit-image argparse deap opencv-python scoop
WORKDIR = /usr/src/
RUN git clone https://github.com/colbrydi/see-segment
RUN mv ./see-segment/see ./see
COPY web_pages/ ./web_pages
COPY public/ ./public
COPY server.py ./server.py

EXPOSE 8080

ENTRYPOINT ["python", "server.py"]