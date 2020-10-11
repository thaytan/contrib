import os

from conans import *


class BisonConan(ConanFile):
    description = "Bison is a general-purpose parser generator"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "clang/[^10.0.1]",
        "make/[^4.3]",
    )
    requires = ("m4/[^1.4.18]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/bison/bison-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"bison-{self.version}")
        autotools.install()

    def package_info(self):
        self.env_info.BISON_PKGDATADIR = os.path.join(self.package_folder, "share", "bison")
