from conans import *


class MpcConan(ConanFile):
    description = "Library for the arithmetic of complex numbers with arbitrarily high precision"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
        "mpfr/[^4.1.0]",
        "gmp/[^6.2.0]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/mpc/mpc-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"{self.name}-{self.version}", args)
        autotools.make()
        autotools.install()
