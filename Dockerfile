FROM python:3.10-bookworm

WORKDIR /finbot
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y software-properties-common && apt-get update
RUN apt-get install -y gcc python3-dev libsqlite3-dev curl

COPY requirements.txt /finbot/

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /finbot/requirements.txt --no-cache-dir

COPY . /finbot