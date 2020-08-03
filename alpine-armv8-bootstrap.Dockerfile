FROM arm64v8/alpine:latest
RUN apk add --no-cache py3-pip make clang cmake git gawk bison rsync
RUN pip3 install --ignore-installed conan