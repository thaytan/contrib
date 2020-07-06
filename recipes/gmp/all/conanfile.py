import os

from conans import *


class GmpConan(ConanFile):
    description = "A free library for arbitrary precision arithmetic"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "bootstrap-cc/[^1.0.0]",
        "m4/[^1.4.18]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://gmplib.org/download/gmp/gmp-{self.version}.tar.xz")

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
