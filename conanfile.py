#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Conan receipt package for USB Library
"""
import os
from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools


class LibUSBConan(ConanFile):
    """Download libusb source, build and create package
    """
    name = "libusb"
    version = "1.0.22"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "udev": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "udev=False", "fPIC=True"
    default_user = "bincrafters"
    url = "http://github.com/bincrafters/conan-libusb"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "LGPL-2.1"
    description = "A cross-platform library to access USB devices"
    exports = ["LICENSE.md"]
    folder_name = name + "-" + version
    no_copy_source = True

    def source(self):
        tools.get("https://github.com/libusb/libusb/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ['--enable-shared' if self.options.shared else '--disable-shared']
        args.append('--enable-static' if not self.options.shared else '--disable-static')
        args.append('--enable-udev' if self.options.udev else '--disable-udev')
        with tools.chdir(os.path.join(self.source_folder, self.folder_name)):
            self.run("autoreconf -i")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(args=["install"])

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_LIBUSB_1_0_PREFIX = self.package_folder
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
