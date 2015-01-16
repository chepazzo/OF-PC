## Dockerfile for dnspc
## Use this to create a docker image
##
## Run Docker image as:
## sudo docker run -dit -p=0.0.0.0:5000:5000 -p 0.0.0.0:53:53/tcp -p 0.0.0.0:53:53/udp dnspc
##
FROM ubuntu:14.04

MAINTAINER Mike Biancaniello

## Base package installs
RUN apt-get update && apt-get install -y git python-pip
RUN mkdir -p /var/lib/dnspc/
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

## Base package src
COPY dnspc /src/dnspc/

## Create startup script
#RUN mkdir -p /usr/local/bin && ln -sf /src/dnspc/start_server.py /usr/local/bin/start_dnspc

## Package config file
COPY config/dnspc.example.conf /etc/dnspc.conf

## LSB init script
COPY install/dnspc /etc/init.d/

#RUN pip install git+https://github.com/chepazzo/dnspc.git

#RUN echo "dnspc ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/dnspc && \
#    chmod 0440 /etc/sudoers.d/dnspc
#
#RUN adduser --system --no-create-home --disabled-password --disabled-login --group dnspc
#
#RUN mkdir -p /var/lib/dnspc
#RUN chown dnspc:dnspc /var/lib/dnspc -R


EXPOSE 5000
EXPOSE 53/tcp
EXPOSE 53/udp

## TODO: eventually, I want this to run as dnspc
#USER dnspc
#CMD ["/usr/local/bin/start_dnspc"]
CMD ["/src/dnspc/start_server.py"]# >> /var/log/dnspc.log
#CMD ["/etc/init.d/dnspc","start"]
