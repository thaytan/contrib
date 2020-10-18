from conans import *


class LibxauConan(ConanFile):
    description = "X11 authorisation library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
    )
    requires = (
        "base/[^1.0.0]",
        "xorgproto/[^2019.1]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXau-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXau-" + self.version):
            autotools.configure(args=args)
            autotools.install()
