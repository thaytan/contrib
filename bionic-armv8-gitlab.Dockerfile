# docker build -f bionic-armv8-gitlab.Dockerfile .
FROM lukechannings/deno:v1.14.3 AS deno
FROM arm64v8/ubuntu:bionic AS builder
RUN apt update && \
    apt install --no-install-recommends -y python3-pip python3-setuptools gcc libpython3.6-dev
RUN CC=/usr/bin/gcc pip3 install --upgrade conan

FROM arm64v8/ubuntu:bionic
COPY --from=builder /usr/local/bin/conan /usr/local/bin/conan
COPY --from=builder /usr/local/lib/python3.6/dist-packages /usr/local/lib/python3.6/dist-packages
COPY --from=deno /bin/deno /usr/bin/deno
RUN apt update && \
  apt install --no-install-recommends -y libc6-dev libatomic1 python3-minimal python3-pkg-resources ca-certificates git-lfs && \
  rm -rf /var/lib/apt/lists/*