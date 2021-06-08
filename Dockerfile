FROM python:3.7-alpine
MAINTAINER Jonathan Tissot

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache python3-dev openssl-dev libffi-dev bash

RUN pip install -r /requirements.txt

RUN mkdir /vmcaws
WORKDIR /vmcaws
COPY . /vmcaws

RUN adduser -D vmcaws
RUN chown vmcaws:vmcaws -R /vmcaws/
USER vmcaws

