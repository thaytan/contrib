# docker build -f <IMAGE> .
FROM alpine:latest AS builder
RUN apk add --no-cache py3-pip
RUN pip3 install --prefix /usr/local --ignore-installed conan

FROM alpine:latest
COPY --from=builder /usr/local/bin/conan /usr/local/bin/conan
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
RUN apk add --no-cache python3