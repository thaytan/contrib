from glob import glob
from os import path, remove

from conans import *


class LibUSBConan(ConanFile):
    description = "A cross-platform library to access USB devices"
    license = "LGPL-2.1"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {"udev": [True, False]}
    default_options = "udev=False"
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"https://github.com/libusb/libusb/releases/download/v{self.version}/libusb-{self.version}.tar.bz2")

    def build(self):
        args = ["--disable-static"]
        args.append("--enable-udev" if self.options.udev else "--disable-udev")
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
