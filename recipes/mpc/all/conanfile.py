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
    requires = ("mpfr/[^4.0.2]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/mpc/mpc-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
