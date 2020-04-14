#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile, CMake, tools

class DepthMetaConan(ConanFile):
    name = "gstreamer-depth-meta"
    license = "Apache 2.0"
    description = "Library to stream depth video"
    url = "https://aivero.com"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "src/*"]

    def set_version(self):
        git = tools.Git(folder=self.recipe_folder)
        tag, branch = git.get_tag(), git.get_branch()
        self.version = tag if tag and branch.startswith("HEAD") else branch

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % (self.user))

    def requirements(self):
        gst_version = "master" if self.version == "master" else "[~%s]" % "1.16.0"
        gst_channel = "testing" if self.version == "master" else "stable"

        self.requires("gstreamer-plugins-base/%s@%s/%s" % (gst_version, self.user, gst_channel))

    def build(self):
        env = {
            "GIT_PKG_VER": "%s" % self.version,
        }
        with tools.environment_append(env):
            cmake = CMake(self)
            cmake.configure()
            cmake.install()