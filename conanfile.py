#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile, CMake, tools

def get_version():
    git = tools.Git()
    try:
        if git.get_tag():
            return git.get_tag()
        else:
            return git.get_branch()
    except:
        return None

class DepthMetaConan(ConanFile):
    name = "gstreamer-depth-meta"
    license = "Apache 2.0"
    version = get_version()
    description = "Library to stream depth video"
    url = "https://aivero.com"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "src/*"]
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % (self.user))

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("gstreamer/[>=1.16.0]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[>=1.16.0]@%s/stable" % self.user)

    def build(self):
        env = {
            "GIT_PKG_VER": "%s" % self.version,
        }
        with tools.environment_append(env):
            cmake = CMake(self)
            cmake.configure()
            cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*-meta.c", "src")
            self.copy("*-meta.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")