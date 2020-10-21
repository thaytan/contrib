import os
from conans import *


class LibVpxConan(ConanFile):
    description = "WebM VP8/VP9 Codec SDK"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        tools.get(f"https://github.com/webmproject/libvpx/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--enable-shared",
            "--disable-static",
            "--disable-examples",
            "--disable-install-docs",
            "--disable-install-srcs",
        ]
        os.environ["STRIP"] = "no"
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libvpx-{self.version}", args)
        autotools.install()
