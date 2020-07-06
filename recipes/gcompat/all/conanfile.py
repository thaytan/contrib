from conans import *


class GcompatConan(ConanFile):
    name = "gcompat"
    description = "The GNU C Library compatibility layer for musl"
    license = "NCSA"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("clang-bootstrap/[^10.0.0]",)

    def source(self):
        tools.get(f"https://distfiles.adelielinux.org/source/gcompat/gcompat-{self.version}.tar.xz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            autotools.install()
