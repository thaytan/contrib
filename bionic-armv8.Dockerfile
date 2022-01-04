FROM lukechannings/deno:v1.14.3 AS deno
FROM arm64v8/ubuntu:bionic AS builder
RUN apt update && \
    apt install --no-install-recommends -y python3-pip python3-setuptools gcc libpython3.6-dev
RUN CC=/usr/bin/gcc pip3 install --upgrade conan MarkupSafe==1.1.1

FROM arm64v8/ubuntu:bionic
COPY --from=builder /usr/local/bin/conan /usr/local/bin/conan
COPY --from=builder /usr/local/lib/python3.6/dist-packages /usr/local/lib/python3.6/dist-packages
COPY --from=deno /bin/deno /usr/bin/deno
RUN apt update && \
  apt install --no-install-recommends -y libc6-dev libatomic1 python3-minimal python3-pkg-resources ruby ca-certificates git-lfs && \
  rm -rf /var/lib/apt/lists/*
RUN DEBIAN_FRONTEND=noninteractive gem install -f asciidoctor-pdf --pre
RUN conan config install https://codeload.github.com/aivero/conan-config/zip/master -sf conan-config-master
RUN conan config set general.default_profile=linux-armv8
RUN conan install git/2.30.0@ -g tools -if /usr/local/bin && \
    # conan install git-lfs/2.13.3@ -g tools -if /usr/local/bin && \
    conan install rust/1.0.0@ && \
    chmod -R 777 /root