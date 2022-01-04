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
RUN apt update && \
  apt install --no-install-recommends -y libc6-dev libatomic1 python3-minimal python3-pkg-resources ruby ca-certificates git git-lfs  && \
  rm -rf /var/lib/apt/lists/*
RUN DEBIAN_FRONTEND=noninteractive gem install -f asciidoctor-pdf --pre
RUN conan config install https://github.com/aivero/conan-config/archive/refs/heads/gitlab.zip -sf conan-config-gitlab
RUN conan config set general.default_profile=linux-x86_64
