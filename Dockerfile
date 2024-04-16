FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy 

RUN mkdir -p /usr/src/app

COPY . /usr/src/app

WORKDIR /usr/src/app