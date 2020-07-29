# docker build -f bionic-armv8-bootstrap.Dockerfile .
FROM ubuntu:bionic AS builder_amd64
RUN apt update && \
  apt install --no-install-recommends -y qemu-user-static

FROM ubuntu:bionic AS builder
COPY --from=builder_amd64 /usr/bin/qemu-aarch64-static /usr/bin/qemu-aarch64-static
RUN apt update && \
    apt install --no-install-recommends -y python3-pip python3-setuptools gcc libpython3.6-dev
RUN CC=/usr/bin/gcc pip3 install --upgrade conan

FROM arm64v8/ubuntu:bionic
COPY --from=builder_amd64 /usr/bin/qemu-aarch64-static /usr/bin/qemu-aarch64-static
COPY --from=builder /usr/local/bin/conan /usr/local/bin/conan
COPY --from=builder /usr/local/lib/python3.6/dist-packages /usr/local/lib/python3.6/dist-packages
RUN apt update && \
  apt install --no-install-recommends -y make gcc-7 g++-7 build-essential git ca-certificates python3-minimal python3-pkg-resources && \
  rm -rf /var/lib/apt/lists/*
