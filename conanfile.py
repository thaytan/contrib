#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Conan receipt package for USB Library
"""
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class LibXorgUtilMacrosConan(ConanFile):
    name = "xorg-util-macros"
    version = "1.19.1"
    default_user = "bincrafters"
    url = "https://github.com/freedesktop/xorg-macros"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "custom"
    description = "X.Org Autotools macros"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False",
    source_subfolder = "source_subfolder"
    exports = ["LICENSE.md"]

    def source(self):
        tools.get("https://github.com/freedesktop/xorg-macros/archive/util-macros-%s.tar.gz" % self.version)
        os.rename("xorg-macros-util-macros-%s" % self.version, self.source_subfolder)

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.chdir(self.source_subfolder):
            self.run("autoreconf -i")
            env_build.configure()
            env_build.make()
            env_build.make(args=["install"])

    def package(self):
        self.copy("COPYING", src=self.source_subfolder, dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
