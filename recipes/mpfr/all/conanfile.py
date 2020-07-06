import os

from conans import *


class MpfrConan(ConanFile):
    name = "mpfr"
    description = "Multiple-precision floating-point library"
    license = "LGPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "bootstrap-cc/[^1.0.0]",
        "make/[^4.3]",
    )
    requires = (
        "base/[^1.0.0]",
        "gmp/[^6.1.2]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/mpfr/mpfr-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
