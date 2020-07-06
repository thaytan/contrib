import os

from conans import *


class IslConan(ConanFile):
    description = "Library for manipulating sets and relations of integer points bounded by linear constraints"
    license = "MIT"
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
        tools.get(f"http://isl.gforge.inria.fr/isl-{self.version}.tar.xz")

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
