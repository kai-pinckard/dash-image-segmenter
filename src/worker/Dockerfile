FROM python:3.8.3

RUN apt-get update && apt-get install -y git
RUN pip install numpy scikit-image argparse deap opencv-python scoop requests

WORKDIR = /usr/src/
RUN git clone https://github.com/colbrydi/see-segment
RUN mv ./see-segment/see ./see
COPY segment_container.py ./segment_container.py

ENTRYPOINT ["python", "segment_container.py", "-l", "cluster"]