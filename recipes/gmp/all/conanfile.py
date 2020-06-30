import os

from conans import *


class GmpConan(ConanFile):
    description = "A free library for arbitrary precision arithmetic"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "bootstrap-gcc/[^7.4.0]",
        "m4/[^1.4.18]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get("https://gmplib.org/download/gmp/gmp-%s.tar.xz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
