from conans import *


class LibuuidConan(ConanFile):
    description = "Portable uuid C library"
    license = "BSD-3-Clause"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"https://netix.dl.sourceforge.net/project/libuuid/libuuid-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libuuid-{self.version}", args)
        autotools.make()
        autotools.install()
