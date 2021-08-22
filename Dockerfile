# Use the official lightweight Python image.
# https://hub.docker.com/_/python
#FROM python:3.7-slim
FROM nvidia/cuda:11.3.0-cudnn8-runtime-ubuntu20.04

ENV GOOGLE_APPLICATION_CREDENTIALS "./token.json"

RUN rm /etc/apt/sources.list.d/*.list && sed -i 's/http:\/\/archive.ubuntu.com/http:\/\/mirrors.sjtug.sjtu.edu.cn/g' /etc/apt/sources.list && apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install production dependencies.
COPY requirements.txt .
RUN pip install --trusted-host mirrors.sjtug.sjtu.edu.cn -i http://mirrors.sjtug.sjtu.edu.cn/pypi/web/simple -U pip setuptools && \
    pip install --trusted-host mirrors.sjtug.sjtu.edu.cn -i http://mirrors.sjtug.sjtu.edu.cn/pypi/web/simple -r requirements.txt

COPY . ./

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 app:app
