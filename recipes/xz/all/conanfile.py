import os

from conans import *


class XzConan(ConanFile):
    description = "Library and command line tools for XZ and LZMA compressed files"
    license = "custom", "GPL", "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://tukaani.org/xz/xz-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()
