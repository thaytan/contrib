FROM arm64v8/alpine:latest
RUN apk add --no-cache musl-dev py3-pip make gcc g++ binutils cmake git gawk bison rsync
RUN pip3 install --ignore-installed conan