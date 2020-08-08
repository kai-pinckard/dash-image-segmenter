From python:3.8.3

RUN apt-get update && apt-get install -y git
WORKDIR = /usr/src/
COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
RUN git clone https://github.com/colbrydi/see-segment
RUN mv ./see-segment/see ./see
COPY app.py ./app.py
COPY components.py ./components.py
COPY tasks.py ./tasks.py

RUN export C_FORCE_ROOT=true

EXPOSE 8888

ENTRYPOINT ["celery", "-A", "tasks", "worker", "--loglevel=info"]