#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile, CMake, tools

class DepthMetaConan(ConanFile):
    name = "gstreamer-depth-meta"
    license = "Apache 2.0"
    description = "Library to stream depth video"
    url = "https://aivero.com"
    settings = "os", "arch", "compiler", "build_type", "gstreamer"
    version = tools.get_env("GIT_TAG", "master")
    exports_sources = ["CMakeLists.txt", "src/*"]

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % (self.user))

    def requirements(self):
        self.requires("gstreamer-plugins-base/[~%s]@%s/stable" % (self.settings.gstreamer, self.user))

    def build(self):
        env = {
            "GIT_PKG_VER": "%s" % self.version,
        }
        with tools.environment_append(env):
            cmake = CMake(self)
            cmake.configure()
            cmake.install()
