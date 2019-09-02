#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile

class GstreamerNvPluginsConan(ConanFile):
    name = "gstreamer-nv-plugins"
    version = "32.2.1"
    url = "http://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = ("Demo conan package")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["lib/gstreamer-1.0/*.so"]
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def package(self):
        self.copy("*.so")
