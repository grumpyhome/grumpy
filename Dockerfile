FROM ubuntu:20.04


# Installing Python 2, because Grumpy is not ported to Python 3 yet

# Go for run-time pulls tzdata, which asks interactive questions
# https://stackoverflow.com/questions/44331836/apt-get-install-tzdata-noninteractive
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    golang \
    make \
    python2-dev \
  && rm -rf /var/lib/apt/lists/*
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python2 get-pip.py


COPY . /app
WORKDIR /app


# Install tools in editable mode. Some `grumpy` commands need run-time, and
# run-time needs at least `grumpy run` to be built.
RUN cd grumpy-tools-src && pip install --editable .

# Install run-time in non-editable mode
RUN cd grumpy-runtime-src && pip install .

