FROM python:3.6-alpine

MAINTAINER Adrian Moreno <adrian.moreno@emc.com>

COPY . /usr/src/app

RUN git clone https://github.com/VxRackNeutrino/tweepy.git
RUN cd tweepy
RUN python setup.py install
RUN pip install -r requirements.txt


WORKDIR /usr/src/app

ENTRYPOINT [ "python", "./listener.py" ]
