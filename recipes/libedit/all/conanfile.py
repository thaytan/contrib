import os

from conans import *


class LibeditConan(ConanFile):
    description = "System V Release 4.0 curses emulation library"
    license = "Zlib"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
    )
    requires = (
        "base/[^1.0.0]",
        "ncurses/[^6.1]",
    )

    def source(self):
        tools.get(f"https://thrysoee.dk/editline/libedit-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
