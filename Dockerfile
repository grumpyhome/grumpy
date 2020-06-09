FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python2 \
  && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

