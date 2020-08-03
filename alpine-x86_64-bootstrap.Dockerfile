FROM alpine:latest
RUN apk add --no-cache py3-pip make clang binutils cmake git gawk bison rsync
RUN pip3 install --ignore-installed conan