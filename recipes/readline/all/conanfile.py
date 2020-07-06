import os

from conans import *


class ReadlineConan(ConanFile):
    description = "GNU readline library"
    license = "GPL-3.0-or-later"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("cc/[^1.0.0]",)
    requires = (
        "base/[^1.0.0]",
        "ncurses/[^6.1]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/readline/readline-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()
