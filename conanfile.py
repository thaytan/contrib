#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class FreetypeConan(ConanFile):
    name = "freetype"
    version = "2.10.1"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "FreeType is a software library to render fonts"
    license = "GPL2"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://git.savannah.gnu.org/cgit/freetype/freetype2.git/snapshot/freetype2-VER-%s.tar.gz" % self.version.replace(".", "-"))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("freetype2-VER-" + self.version.replace(".", "-")):
            self.run("./autogen.sh")
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
