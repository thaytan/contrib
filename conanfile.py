#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conans import ConanFile, CMake, tools


class GTestConan(ConanFile):
    name = "gtest"
    version = "1.8.1"
    description = "Google's C++ test framework"
    url = "http://github.com/bincrafters/conan-gtest"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/google/googletest/archive/release-%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        cmake.configure(source_folder="googletest-release-" + self.version)
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
