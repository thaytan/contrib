from conans import *


class LibxrenderConan(ConanFile):
    name = "libxrender"
    description = "X Rendering Extension client library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "pkgconf/[^1.6.3]",
        "xorg-util-macros/[^1.19.1]",
        "xtrans/[^1.4.0]",
    )
    requires = (
        "base/[^1.0.0]",
        "libx11/[^1.6.8]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXrender-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"libXrender-{self.version}"):
            autotools.configure(args=args)
            autotools.install()
