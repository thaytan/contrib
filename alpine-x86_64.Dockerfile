FROM alpine:latest
RUN apk add --no-cache py3-pip
RUN pip3 install --ignore-installed conan