#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class OrcConan(ConanFile):
    name = "orc"
    version = "0.4.29"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "udev": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "udev=False", "fPIC=True"
    default_user = "bincrafters"
    url = "http://github.com/bincrafters/conan-orc"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "LGPL-2.1"
    description = "Optimized Inner Loop Runtime Compiler"
    folder_name = name + "-" + version

    def source(self):
        tools.get("https://github.com/GStreamer/orc/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ['--disable-gtk-doc']
        vars = {
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
        }
        with tools.chdir(os.path.join(self.source_folder, self.folder_name)), tools.environment_append(vars):
                self.run("./autogen.sh " + " ".join(args))
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure(args=args)
                autotools.make()
                autotools.make(args=["install"])

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
