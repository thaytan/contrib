from conans import *


class MpfrConan(ConanFile):
    description = "Multiple-precision floating-point library"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
        "gmp/[^6.2.0]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/mpfr/mpfr-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"mpfr-{self.version}", args)
        autotools.make()
        autotools.install()
