#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class YasmConan(ConanFile):
    name = "yasm"
    version = "1.3.0"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Yasm is a complete rewrite of the NASM assembler under the “new” BSD License"
    license = "BSD"
    settings = "os_build", "arch_build", "compiler"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("http://www.tortall.net/projects/yasm/releases/yasm-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()
