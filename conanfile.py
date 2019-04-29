#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class LibVpxConan(ConanFile):
    name = "libvpx"
    version = "1.8.0"
    url = "https://github.com/webmproject/libvpx"
    author = "Prozum"
    description = "WebM VP8/VP9 Codec SDK"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    def source(self):
        tools.get("https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version)

    def build_requirements(self):
        self.build_requires("yasm_installer/1.3.0@%s/%s" % (self.user, self.channel))

    def build(self):
        args = []
        with tools.chdir("libvpx-" + self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")

