# docker build --build-arg=OS_VERSION=bionic --build-arg=RGBD_TOOLKIT_VERSION=1.5.0 -t aivero-rgbd-toolkit .
ARG OS_VERSION=bionic

FROM ubuntu:$OS_VERSION

RUN apt-get update && \
  apt-get install --no-install-recommends -y python3-pip python3-setuptools python3-dev python3-venv python3-wheel git && \
  pip3 install --upgrade conan

RUN conan config install https://github.com/aivero/conan-config.git
RUN conan config set general.default_profile=linux-x86_64

WORKDIR /WORKDIR

ARG RGBD_TOOLKIT_VERSION=1.5.0
ENV CI_COMMIT_REF_SLUG=${RGBD_TOOLKIT_VERSION}

RUN git clone https://gitlab.com/aivero/contrib.git -b ${RGBD_TOOLKIT_VERSION}

WORKDIR /WORKDIR/contrib

RUN conan create aivero-rgbd-toolkit
RUN conan install aivero-rgbd-toolkit/${RGBD_TOOLKIT_VERSION}@ -if /opt/aivero/rgbd_toolkit

WORKDIR /opt/aivero/rgbd_toolkit
COPY entry.sh .

CMD [ "bash", "entry.sh" ]
