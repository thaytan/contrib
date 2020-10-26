from conans import *


class LibpthreadStubsConan(ConanFile):
    description = "X11 client-side library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        tools.get(f"https://xcb.freedesktop.org/dist/libpthread-stubs-{self.version}.tar.bz2")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libpthread-stubs-{self.version}")
        autotools.install()
