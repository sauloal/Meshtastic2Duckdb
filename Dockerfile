FROM ubuntu:22.04

RUN apt clean all \
&&  apt update \
&&  apt install -y make python3-venv curl \
&&  apt clean all

COPY ./requirements.txt ./Makefile /data/

WORKDIR /data

RUN make venv install

COPY ./ /data

