## Dockerfile for dnspc
## Use this to create a docker image
##
## Run Docker image as:
## sudo docker run -dit -p=0.0.0.0:5000:5000 -p 0.0.0.0:53:53/tcp -p 0.0.0.0:53:53/udp dnspc
##
FROM ubuntu:14.04

MAINTAINER Mike Biancaniello

WORKDIR /app

RUN apt-get update && apt-get install -y git python-pip openssh-server
RUN pip install git+https://github.com/chepazzo/dnspc.git

RUN echo "dnspc ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/dnspc && \
    chmod 0440 /etc/sudoers.d/dnspc

RUN adduser --system --no-create-home --disabled-password --disabled-login --group dnspc

USER dnspc

EXPOSE 5000
EXPOSE 53/tcp
EXPOSE 53/udp
CMD ["sudo","/usr/local/bin/start_dnspc"]
