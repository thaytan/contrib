#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class X265Conan(ConanFile):
    name = "x265"
    version = "2.7"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "https://github.com/someauthor/somelib/blob/master/LICENSES"
    settings = "os", "arch", "compiler", "build_type"
    options = {"bit_depth": [8, 10, 12], "HDR10": [True, False]}
    default_options = "bit_depth=8", "HDR10=False"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/videolan/x265/archive/%s.tar.gz" % self.version)

    def build_requirements(self):
        self.build_requires("yasm/1.3.0@%s/%s" % (self.user, self.channel))

    def build(self):
        cmake = CMake(self, generator='Ninja')
        cmake.definitions['HIGH_BIT_DEPTH'] = self.options.bit_depth != 8
        cmake.definitions['MAIN12'] = self.options.bit_depth == 12
        cmake.definitions['ENABLE_HDR10_PLUS'] = self.options.HDR10
        cmake.configure(source_folder=os.path.join("%s-%s" % (self.name, self.version), "source"))
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = ["x265"]
        self.cpp_info.srcdirs.append("src")
