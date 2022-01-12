FROM python:3.8

RUN apt-get update && apt-get -y install python3-pip

COPY . /blog_api_container

WORKDIR /blog_api_container/

RUN pip install -r blog_api/requirements.txt

ENV PYTHONPATH=`pwd`
ENV MAIL_USERNAME="nhatle253411@gmail.com"
ENV MAIL_PASSWORD="ahihi123@"
ENV MAIL_FROM="your_gmail@gmail.com"
ENV MAIL_PORT="587"
ENV MAIL_SERVER="smtp.gmail.com"
ENV MAIL_FROM_NAME="Email notification for user"
ENV SECRET_KEY="some_random_string"