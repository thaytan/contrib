import os

from conans import *


class MozjpegConan(ConanFile):
    description = "JPEG image codec with accelerated baseline compression and decompression"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/1.0.0",
        "yasm/[^1.3.0]",
        "cmake/[^3.15.3]",
    )

    def source(self):
        tools.get(f"https://github.com/mozilla/mozjpeg/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
        ]

        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("autoreconf -i")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
