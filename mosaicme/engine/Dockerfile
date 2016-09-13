FROM golang:1.6-onbuild

MAINTAINER Magdy Salem <magdy.salem@emc.com>

RUN apt-get install metapixel

RUN apt-get install imagemagick

ADD . /go/src/engine

RUN go install engine

ENTRYPOINT ["/go/bin/engine"]
