FROM quay.io/ncigdc/samtools:1.1

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev \
    build-essential cmake zlib1g-dev libncurses-dev wget

RUN wget https://github.com/genome/somatic-sniper/archive/v1.0.5.0.tar.gz && tar xvzf v1.0.5.0.tar.gz && rm v1.0.5.0.tar.gz
RUN cd somatic-sniper-1.0.5.0 && cmake . && make deps && make -j && make install

ADD multi_somaticsniper.py /bin

ENV multi_somaticsniper v1.2
