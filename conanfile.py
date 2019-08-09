#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment


class ZlibConan(ConanFile):
    name = "zlib"
    version = "1.2.11"
    url = "https://gitlab.com/aivero/public/conan/conan-zlib"
    license = "Zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                   "(Also Free, Not to Mention Unencumbered by Patents)")
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        tools.get("https://github.com/madler/zlib/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = ["z"]
        self.cpp_info.srcdirs.append("src")
