#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class LibUSBConan(ConanFile):
    name = "libusb"
    version = "1.0.22"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    description = "A cross-platform library to access USB devices"
    settings = "os", "compiler", "build_type", "arch"
    options = {"udev": [True, False]}
    default_options = "udev=False"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/libusb/libusb/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        args.append("--enable-udev" if self.options.udev else "--disable-udev")
        with tools.chdir("%s-%s" % (self.name, self.version)):
                self.run("./autogen.sh " + " ".join(args))
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure(args=args)
                autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
