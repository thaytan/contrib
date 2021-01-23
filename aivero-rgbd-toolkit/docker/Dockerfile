# docker build --build-arg=OS_VERSION=bionic --build-arg=RGBD_TOOLKIT_VERSION=1.5.0 -t aivero-rgbd-toolkit .
ARG OS_VERSION=bionic

FROM ubuntu:$OS_VERSION


RUN apt-get update && \
  apt-get install --no-install-recommends -y python3-pip python3-setuptools python3-dev python3-venv python3-wheel git && \
  pip3 install --upgrade conan

RUN conan config install https://gitlab.com/aivero/public/conan/conan-config.git
RUN conan config set general.default_profile=linux_armv8_release

WORKDIR /WORKDIR

ARG RGBD_TOOLKIT_VERSION=1.5.0
ENV CI_COMMIT_REF_SLUG=${RGBD_TOOLKIT_VERSION}

RUN git clone https://gitlab.com/aivero/public/aivero-rgbd-toolkit.git -b ${RGBD_TOOLKIT_VERSION}

WORKDIR /WORKDIR/aivero-rgbd-toolkit

RUN conan create . aivero/stable
RUN conan install aivero_rgbd_toolkit/${RGBD_TOOLKIT_VERSION}@aivero/stable -if /opt/aivero/rgbd_toolkit

WORKDIR /opt/aivero/rgbd_toolkit
COPY entry.sh .

CMD [ "bash", "entry.sh" ]
