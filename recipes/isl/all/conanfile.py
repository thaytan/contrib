import os

from conans import *


class IslConan(ConanFile):
    description = "Library for manipulating sets and relations of integer points bounded by linear constraints"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/[^7.4.0]")
        self.build_requires("make/[^4.3]")

    def requirements(self):
        self.requires("gmp/[^6.1.2]")

    def source(self):
        tools.get("http://isl.gforge.inria.fr/isl-%s.tar.xz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
