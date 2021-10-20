# docker build -f bionic-x86_64.Dockerfile .
FROM denoland/deno:bin-1.14.3 AS deno
FROM ubuntu:bionic AS builder
RUN apt update && \
  apt install --no-install-recommends -y python3-pip python3-setuptools && \
  pip3 install --upgrade conan

FROM ubuntu:bionic
COPY --from=builder /usr/local/bin/conan /usr/local/bin/conan
COPY --from=builder /usr/local/lib/python3.6/dist-packages /usr/local/lib/python3.6/dist-packages
COPY --from=deno /deno /usr/bin/deno
RUN apt update && apt install --no-install-recommends -y software-properties-common && add-apt-repository ppa:git-core/ppa && \
  apt update && apt install --no-install-recommends -y make gcc-7 g++-7 libc6-dev cmake git gawk bison rsync python3-minimal python3-pkg-resources python3-distutils && \
  apt remove -y software-properties-common && apt autoremove -y && rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 10
RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 10
