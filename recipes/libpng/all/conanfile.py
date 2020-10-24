from conans import *


class LibpngConan(ConanFile):
    description = "A collection of routines used to create PNG format graphics files"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/1.0.0",
    )
    requires = ("zlib/[^1.2.11]",)

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/sourceforge/libpng/libpng-{self.version}.tar.xz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libpng-{self.version}", args)
        autotools.make()
        autotools.install()
