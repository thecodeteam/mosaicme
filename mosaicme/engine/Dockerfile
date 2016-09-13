FROM golang:1.6-onbuild

MAINTAINER Magdy Salem <magdy.salem@emc.com>

RUN apt-get update &&\
  apt-get -y install metapixel imagemagick &&\
  rm -rf /var/lib/apt/lists/*
