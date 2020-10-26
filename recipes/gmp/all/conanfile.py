from conans import *


class GmpConan(ConanFile):
    description = "A free library for arbitrary precision arithmetic"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "m4/[^1.4.18]",
    )

    def source(self):
        tools.get(f"https://gmplib.org/download/gmp/gmp-{self.version}.tar.xz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"gmp-{self.version}", args)
        autotools.make()
        autotools.install()
