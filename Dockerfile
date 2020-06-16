FROM ubuntu:20.04

# Grumpy is not ported to Python 3 yet
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python2-dev \
  && rm -rf /var/lib/apt/lists/*
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python2 get-pip.py


COPY . /app
WORKDIR /app


# Install in editable mode
RUN cd grumpy-tools-src && pip install --editable .

