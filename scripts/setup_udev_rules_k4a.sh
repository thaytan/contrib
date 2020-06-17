#!/bin/bash -e

# Execute as sudo
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

# Manual setup
echo -e "Downloading latest udev rules for K4A devices...\n"
wget --version &> /dev/null || apt-get install -y wget &> /dev/null
wget https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/master/scripts/99-k4a.rules
mv 99-k4a.rules /etc/udev/rules.d/ && udevadm control --reload-rules && udevadm trigger
echo -e "\e[32mSuccessfuly deployed udev-rules for K4A cameras\n\e[33mPlease replug any attached K4A cameras before continuing\e[0m"
