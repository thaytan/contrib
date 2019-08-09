#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class LibVpxConan(ConanFile):
    name = "libvpx"
    version = "1.8.0"
    url = "https://github.com/webmproject/libvpx"
    description = "WebM VP8/VP9 Codec SDK"
    license = "BSD"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version)

    def build_requirements(self):
        self.build_requires("yasm/1.3.0@%s/%s" % (self.user, self.channel))

    def build(self):
        args = []
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")

