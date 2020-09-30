import os

from conans import *


class ReadlineConan(ConanFile):
    description = "GNU readline library"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
        "ncurses/[^6.1]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/readline/readline-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"{self.name}-{self.version}", args)
        autotools.install()
