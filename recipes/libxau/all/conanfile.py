from conans import *


class LibxauConan(ConanFile):
    description = "X11 authorisation library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
    )
    requires = ("xorgproto/[^2020.1]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXau-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-shared"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libXau-{self.version}", args)
        autotools.install()
