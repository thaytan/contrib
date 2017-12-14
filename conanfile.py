#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibX265Conan(ConanFile):
    name = "libx265"
    version = "2.6"
    url = "https://github.com/bincrafters/conan-libname"
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "https://github.com/someauthor/somelib/blob/master/LICENSES"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = ['cmake']

    def build_requirements(self):
        self.build_requires("yasm_installer/[>=1.3.0]@bincrafters/stable")
        self.build_requires("ninja_installer/[>=1.8.2]@bincrafters/stable")

    def source(self):
        source_url = "https://bitbucket.org/multicoreware/x265/downloads/x265_%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = 'x265_v%s' % self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        cmake = CMake(self, generator='Ninja')
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        # TODO : figure out how to properly set this on earlier stage, so CMAKE_SIZE_OF_VOID_P is correct
        if self.settings.os == "Linux" and self.settings.arch == 'x86':
            cmake.definitions['CMAKE_C_FLAGS'] = '-m32'
            cmake.definitions['CMAKE_CXX_FLAGS'] = '-m32'
            cmake.definitions['CMAKE_SHARED_LINKER_FLAGS'] = '-ldl'
            cmake.definitions['CMAKE_EXE_LINKER_FLAGS'] = '-ldl'
        if self.settings.os == "Macos":
            cmake.definitions['CMAKE_SHARED_LINKER_FLAGS'] = '-Wl,-read_only_relocs,suppress'
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="COPYING", src='sources')

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(['dl', 'pthread'])
