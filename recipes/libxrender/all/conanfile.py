from conans import *


class LibxrenderConan(ConanFile):
    description = "X Rendering Extension client library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "xorg-util-macros/[^1.19.2]",
        "xtrans/[^1.4.0]",
    )
    requires = ("libx11/[^1.6.12]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXrender-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libXrender-{self.version}", args)
        autotools.install()
