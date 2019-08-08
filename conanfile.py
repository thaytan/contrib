#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class FlexConan(ConanFile):
    name = "flex"
    version = "2.6.4"
    url = "https://github.com/bincrafters/conan-flex"
    homepage = "https://github.com/westes/flex"
    description = "Flex, the fast lexical analyzer generator"
    license = "BSD 2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("bison/3.3@%s/%s" % (self.user, self.channel), private=True)

    def source(self):
        tools.get("https://github.com/westes/flex/releases/download/v{0}/flex-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--enable-shared", "--disable-nls", "ac_cv_func_reallocarray=no"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("./autogen.sh")
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
