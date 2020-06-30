#!/bin/bash -e

# Execute as sudo
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

# Manual setup
echo -e "Downloading latest udev rules for K4A devices...\n"
wget --version &> /dev/null || (>&2 echo -e "\e[31mDownloading udev rules failed, please install `wget`\n\e[0m\t& sudo apt-get install wget"; exit 1)
wget https://raw.githubusercontent.com/microsoft/Azure-Kinect-Sensor-SDK/master/scripts/99-k4a.rules
mv 99-k4a.rules /etc/udev/rules.d/ && udevadm control --reload-rules && udevadm trigger
echo -e "\e[32mSuccessfuly deployed udev-rules for K4A cameras\n\e[33mPlease replug any attached K4A cameras before continuing\e[0m"
