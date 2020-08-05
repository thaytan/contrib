FROM alpine:latest
RUN apk add --no-cache musl-dev linux-headers py3-pip make gcc g++ binutils binutils-gold zlib cmake git gawk bison rsync
RUN pip3 install --ignore-installed conan