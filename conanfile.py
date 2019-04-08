#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil


class X265Conan(ConanFile):
    name = "x265"
    version = "2.7"
    homepage = "http://x265.org"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/bincrafters/conan-libx265"
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "https://github.com/someauthor/somelib/blob/master/LICENSES"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "bit_depth": [8, 10, 12], "HDR10": [True, False]}
    default_options = "shared=False", "fPIC=True", "bit_depth=8", "HDR10=False"
    generators = ['cmake']

    def source(self):
        tools.get("https://github.com/videolan/x265/archive/%s.tar.gz" % self.version)

    def build_requirements(self):
        self.build_requires("yasm_installer/1.3.0@%s/%s" % (self.user, self.channel))

    def build(self):
        cmake = CMake(self, generator='Ninja')
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['HIGH_BIT_DEPTH'] = self.options.bit_depth != 8
        cmake.definitions['MAIN12'] = self.options.bit_depth == 12
        cmake.definitions['ENABLE_HDR10_PLUS'] = self.options.HDR10
        cmake.configure(source_folder=os.path.join("x265-" + self.version, "source"))
        cmake.build()
        cmake.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
