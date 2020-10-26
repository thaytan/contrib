from conans import *


class Libxxf86vmConan(ConanFile):
    description = "X11 XFree86 video mode extension library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.2]",
        "xorgproto/[^2020.1]",
    )
    requires = ("libxext/[^1.3.4]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXxf86vm-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libXxf86vm-{self.version}", args)
        autotools.install()
