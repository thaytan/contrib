from conans import *


class LibpthreadStubsConan(ConanFile):
    description = "X11 client-side library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://xcb.freedesktop.org/dist/libpthread-stubs-{self.version}.tar.bz2")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()
