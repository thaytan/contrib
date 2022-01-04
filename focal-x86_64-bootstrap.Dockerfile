FROM denoland/deno:bin-1.14.3 AS deno
FROM ubuntu:focal AS builder
RUN apt update && \
  apt install --no-install-recommends -y python3-pip python3-setuptools && \
  pip3 install --upgrade conan
FROM ubuntu:focal
COPY --from=builder /usr/local/bin/conan /usr/local/bin/conan
COPY --from=builder /usr/local/lib/python3.8/dist-packages /usr/local/lib/python3.8/dist-packages
COPY --from=deno /deno /usr/bin/deno
RUN apt update \
  apt install --no-install-recommends -y make clang clang++ libc6-dev cmake git gawk bison python3-minimal python3-pkg-resources python3-distutils && \
  rm -rf /var/lib/apt/lists/*