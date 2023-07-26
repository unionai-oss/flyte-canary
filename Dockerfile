FROM docker as docker
FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y  git build-essential \
 apt-transport-https ca-certificates curl  \
 software-properties-common iptables net-tools \
 openssl pigz jq


RUN update-alternatives --set iptables /usr/sbin/iptables-legacy
RUN update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

RUN mkdir /certs /certs/client && chmod 1777 /certs /certs/client


ENV PATH=$PATH:/root

COPY execute.sh /root/execute.sh
COPY config.yaml /root/.uctl/config.yaml

COPY --from=docker /usr/local/bin/ /usr/local/bin/

VOLUME /var/lib/docker


ENV PATH="/usr/local/bin:$PATH"

WORKDIR /root