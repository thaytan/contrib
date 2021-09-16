#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Conan recipe package for Google FlatBuffers
"""
import os
import shutil
from conans import ConanFile, CMake, tools
from build import *
 
class FlatbuffersConan(Recipe):
    name = "flatbuffers"
    license = "Apache"
    description = "Memory Efficient Serialization Library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = ["CMake/*", "include/*", "src/*", "grpc/*", "CMakeLists.txt", "conan/CMakeLists.txt"]

    def source(self):
        self.get(f"https://github.com/google/flatbuffers/archive/refs/tags/v{self.version}.tar.gz")
        """Wrap the original CMake file to call conan_basic_setup
        """
        with tools.chdir(f"flatbuffers-{self.version}.src"):
            shutil.move("CMakeLists.txt", "CMakeListsOriginal.txt")
            shutil.move(os.path.join("conan", "CMakeLists.txt"), "CMakeLists.txt")

    def configure_cmake(self):
        """Create CMake instance and execute configure step
        """
        cmake = CMake(self)
        cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = self.options.shared
        cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = not self.options.shared
        cmake.configure(source_folder=f"flatbuffers-{self.version}.src")
        return cmake

    def build(self):
        """Configure, build and install FlatBuffers using CMake.
        """
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        """Copy Flatbuffers' artifacts to package folder
        """
        cmake = self.configure_cmake()
        cmake.install()
        self.copy(pattern="FindFlatBuffers.cmake", dst=os.path.join("lib", "cmake", "flatbuffers"), src="CMake")
        self.copy(pattern="flathash*", dst="bin", src="bin")
        self.copy(pattern="flatc*", dst="bin", src="bin")
        self.copy(pattern="*.a", dst="lib", src="lib")
        self.copy(pattern="*.pc", dst="lib", src="lib/pkgconfig")

    def package_info(self):
        """Collect built libraries names and solve flatc path.
        """
        self.cpp_info.libs = tools.collect_libs(self)
        self.user_info.flatc = os.path.join(self.package_folder, "bin", "flatc")