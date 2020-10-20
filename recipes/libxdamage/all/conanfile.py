from conans import *


class LibxdamageConan(ConanFile):
    description = "X11 damaged region extension library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )
    requires = ("libxfixes/[^5.0.3]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXdamage-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libXdamage-{self.version}", args)
        autotools.install()
