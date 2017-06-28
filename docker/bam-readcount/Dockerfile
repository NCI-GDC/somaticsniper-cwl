FROM ubuntu:14.04

MAINTAINER Shenglai Li <sli6@uchicago.edu>

USER root
RUN apt-get update && apt-get install -y --force-yes build-essential git-core cmake zlib1g-dev libncurses-dev patch

ENV HOME /home/ubuntu

WORKDIR ${HOME}

RUN git clone https://github.com/genome/bam-readcount.git \
    && cmake ~/bam-readcount \
    && make -j && make install
