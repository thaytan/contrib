# docker build -f dispatch.Dockerfile .
FROM ubuntu:bionic AS builder
RUN apt update && \
  apt install --no-install-recommends -y python3-pip python3-setuptools && \
  pip3 install --upgrade conan

FROM ubuntu:bionic
COPY --from=builder /usr/local/bin/conan /usr/local/bin/conan
COPY --from=builder /usr/local/lib/python3.6/dist-packages /usr/local/lib/python3.6/dist-packages
RUN apt update && \
  apt install --no-install-recommends -y git nodejs python3-minimal python3-pkg-resources && \
  rm -rf /var/lib/apt/lists/*