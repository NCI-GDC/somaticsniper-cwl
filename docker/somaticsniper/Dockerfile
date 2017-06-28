FROM ubuntu:14.04
USER root
RUN apt-get update && apt-get install -y --force-yes build-essential cmake zlib1g-dev libncurses-dev wget

RUN adduser --disabled-password --gecos '' ubuntu && adduser ubuntu sudo && echo "ubuntu    ALL=(ALL)   NOPASSWD:ALL" >> /etc/sudoers.d/ubuntu

ENV HOME /home/ubuntu
RUN mkdir ${HOME}/bin
WORKDIR ${HOME}/bin

RUN wget https://github.com/genome/somatic-sniper/archive/v1.0.5.0.tar.gz && tar xvzf v1.0.5.0.tar.gz && rm v1.0.5.0.tar.gz
RUN cd  somatic-sniper-1.0.5.0 && cmake . && make deps && make -j && make install

USER ubuntu

ENV PATH ${PATH}:${HOME}/bin/

WORKDIR ${HOME}
