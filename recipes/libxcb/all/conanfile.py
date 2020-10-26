from conans import *


class LibxcbConan(ConanFile):
    description = "X11 client-side library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "xcb-proto/[^1.13]",
        "libpthread-stubs/[^0.4]",
    )
    requires = ("libxau/[^1.0.9]",)

    def source(self):
        tools.get(f"https://xcb.freedesktop.org/dist/libxcb-{self.version}.tar.xz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libxcb-{self.version}", args)
        autotools.install()
