from conans import *


class LibxextConan(ConanFile):
    description = "X11 miscellaneous extensions library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "xorg-util-macros/[^1.19.2]",
    )
    requires = ("libx11/[^1.6.12]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXext-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libXext-{self.version}", args)
        autotools.install()
