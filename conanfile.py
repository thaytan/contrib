#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibX265Conan(ConanFile):
    name = "libx265"
    version = "2.6"
    url = "https://github.com/bincrafters/conan-libx265"
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "https://github.com/someauthor/somelib/blob/master/LICENSES"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = ['cmake']

    def source(self):
        source_url = "https://bitbucket.org/multicoreware/x265/downloads/x265_%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = 'x265_v%s' % self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            with tools.vcvars(self.settings, filter_known_paths=False):
                self.build_cmake()
        else:
            self.build_cmake()

    def build_cmake(self):
        cmake = CMake(self, generator='Ninja')
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
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
