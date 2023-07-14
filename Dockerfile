FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y \
    git build-essential apt-transport-https ca-certificates curl software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
RUN apt-get update
RUN apt install -y docker.io

COPY execute.sh /root/execute.sh
COPY config.yaml /root/.uctl/config.yaml

WORKDIR /root