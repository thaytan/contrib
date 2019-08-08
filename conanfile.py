#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, Meson, tools
import os


class LibVaConan(ConanFile):
    name = "libva"
    version = "2.3.0"
    description = "Libva is an implementation for VA-API (VIdeo Acceleration API)"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    author = "BinCrafters <bincrafters@gmail.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("libdrm/2.4.96@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/intel/libva/archive/%s.tar.gz" % self.version)

    def build(self):
        meson = Meson(self)
        meson.configure(source_folder="libva-" + self.version)
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
