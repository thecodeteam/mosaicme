FROM golang:1.6.2

MAINTAINER Magdy Salem <magdy.salem@emc.com>

COPY ./sources.list /etc/apt/

RUN apt-get update
RUN apt-get install -y  --force-yes \
    metapixel\
    imagemagick

RUN go get github.com/caarlos0/env
RUN go get github.com/dchest/uniuri
RUN go get github.com/minio/minio-go
RUN go get github.com/streadway/amqp


ADD . /go/src/
WORKDIR /go/src
RUN go build -o /go/bin/engine .
CMD ["/go/bin/engine"]

