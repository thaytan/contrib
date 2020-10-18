from conans import *


class LibxrenderConan(ConanFile):
    description = "X Rendering Extension client library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "pkgconf/[^1.6.3]",
        "xorg-util-macros/[^1.19.1]",
        "xtrans/[^1.4.0]",
    )
    requires = ("libx11/[^1.6.8]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXrender-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"libXrender-{self.version}"):
            autotools.configure(args=args)
            autotools.install()
