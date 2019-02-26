#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment


class ZlibConan(ConanFile):
    name = "zlib"
    version = "1.2.11"
    url = "http://github.com/conan-community/conan-zlib"
    homepage = "https://zlib.net"
    author = "Conan Community"
    license = "Zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                   "(Also Free, Not to Mention Unencumbered by Patents)")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    folder_name = name + "-" + version
    no_copy_source = True

    def source(self):
        tools.get("https://github.com/madler/zlib/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self.folder_name, build_folder="build")
        cmake.build()
        cmake.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = ["z"]
        self.env_info.PKG_CONFIG_ZLIB_PREFIX = self.package_folder
        self.env_info.PKG_CONFIG_ZLIB_EXEC_PREFIX = self.package_folder
        self.env_info.PKG_CONFIG_ZLIB_LIBDIR = os.path.join(self.package_folder, "lib")
        self.env_info.PKG_CONFIG_ZLIB_SHAREDLIBDIR = os.path.join(self.package_folder, "lib")
        self.env_info.PKG_CONFIG_ZLIB_INCLUDEDIR = os.path.join(self.package_folder, "include")
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "share", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
