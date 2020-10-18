from conans import *


class Libxxf86vmConan(ConanFile):
    description = "X11 XFree86 video mode extension library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "pkgconf/[^1.6.3]",
        "xorg-util-macros/[^1.19.1]",
        "xorgproto/[^2019.1]",
    )
    requires = (
        "base/[^1.0.0]",
        "libxext/[^1.3.4]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXxf86vm-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXxf86vm-" + self.version):
            autotools.configure()
            autotools.install()
