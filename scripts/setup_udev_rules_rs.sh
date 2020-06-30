#!/bin/bash -e

# Execute as sudo
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

# Install Debian
echo -e "Installing udev rules for RealSense devices..."
apt-get install -y librealsense2-udev-rules &> /dev/null \
&& echo -e "\e[32mSuccessfuly installed udev-rules for RealSense cameras\n\e[33mPlease replug any attached RealSense cameras before continuing\e[0m" \
&& exit 0

# Manual setup (if Debian installation fails)
echo -e "Installation failed, manually downloading the latest udev rules...\n"
wget --version &> /dev/null || (>&2 echo -e "\e[31mDownloading udev rules failed, please install `wget`\n\e[0m\t& sudo apt-get install wget"; exit 1)
wget https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules
mv 99-realsense-libusb.rules /etc/udev/rules.d/ && udevadm control --reload-rules && udevadm trigger
echo -e "\e[32mSuccessfuly deployed udev-rules for RealSense cameras\n\e[33mPlease replug any attached RealSense cameras before continuing\e[0m"
