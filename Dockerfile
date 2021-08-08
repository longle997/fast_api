FROM python:3.8

RUN apt-get update && apt-get -y install python3-pip

COPY . /blog_api_container

WORKDIR /blog_api_container/

RUN pip install -r blog_api/requirements.txt

ENV PYTHONPATH=`pwd`
