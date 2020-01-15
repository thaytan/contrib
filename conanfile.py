from glob import glob
from os import path, remove

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibUSBConan(ConanFile):
    name = "libusb"
    version = tools.get_env("GIT_TAG", "1.0.23")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    description = "A cross-platform library to access USB devices"
    settings = "os", "compiler", "build_type", "arch"
    options = {"udev": [True, False]}
    default_options = "udev=False"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/libusb/libusb/releases/download/v{0}/libusb-{0}.tar.bz2".format(self.version))

    def build(self):
        args = ["--disable-static"]
        args.append("--enable-udev" if self.options.udev else "--disable-udev")
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
