FROM python:3

RUN apt-get update && apt-get -y install python3-pip

COPY . /blog_api_container

WORKDIR /blog_api_container/

RUN pip install -r blog_api/requirements.txt

ENV PYTHONPATH=`pwd`

# ENTRYPOINT alembic upgrade head

# ENTRYPOINT uvicorn blog_api.main:app --port 8000 --host 0.0.0.0 --reload
