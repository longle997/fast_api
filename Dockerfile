FROM python:3

RUN apt-get update && apt-get -y install python3-pip

COPY /blog_api /blog_api

WORKDIR /blog_api

RUN pip install -r requirements.txt

ENV PYTHONPATH=`pwd`

ENTRYPOINT uvicorn main:app --port 8000 --host 0.0.0.0 --reload

# CMD uvicorn blog_api.main:app --port 8000 --reload
