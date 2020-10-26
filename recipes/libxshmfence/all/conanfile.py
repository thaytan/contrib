from conans import *


class LibxshmfenceConan(ConanFile):
    description = "Library that exposes a event API on top of Linux futexes"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.2]",
    )
    requires = ("xorgproto/[^2020.1]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libxshmfence-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libxshmfence-{self.version}", args)
        autotools.install()
