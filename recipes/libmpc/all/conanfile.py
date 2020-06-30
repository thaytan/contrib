import os

from conans import *


class MpcConan(ConanFile):
    description = "Library for the arithmetic of complex numbers with arbitrarily high precision"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "bootstrap-gcc/[^7.4.0]",
        "make/[^4.3]",
    )
    requires = (
        "gmp/[^6.1.2]",
        "mpfr/[^4.0.2]",
    )

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/mpc/mpc-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
