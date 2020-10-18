import os

from conans import *


class XzConan(ConanFile):
    description = "Library and command line tools for XZ and LZMA compressed files"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"https://tukaani.org/xz/xz-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"xz-{self.version}")
        autotools.install()
