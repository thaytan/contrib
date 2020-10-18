from glob import glob
from os import path, remove

from conans import *


class LibuuidConan(ConanFile):
    description = "Portable uuid C library"
    license = "BSD-3-Clause"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://netix.dl.sourceforge.net/project/libuuid/libuuid-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
