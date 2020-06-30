from glob import glob
from os import path, remove

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibUSBConan(ConanFile):
    description = "A cross-platform library to access USB devices"
    license = "LGPL-2.1"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {"udev": [True, False]}
    default_options = "udev=False"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[^1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/libusb/libusb/releases/download/v{0}/libusb-{0}.tar.bz2".format(self.version))

    def build(self):
        args = ["--disable-static"]
        args.append("--enable-udev" if self.options.udev else "--disable-udev")
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
