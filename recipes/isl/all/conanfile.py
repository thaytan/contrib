from conans import *


class IslConan(ConanFile):
    description = "Library for manipulating sets and relations of integer points bounded by linear constraints"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "gmp/[^6.2.0]",
    )

    def source(self):
        tools.get(f"http://isl.gforge.inria.fr/isl-{self.version}.tar.xz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"isl-{self.version}", args)
        autotools.make()
        autotools.install()
