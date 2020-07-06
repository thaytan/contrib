from conans import *


class LibpthreadStubsConan(ConanFile):
    description = "X11 client-side library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://xcb.freedesktop.org/dist/libpthread-stubs-{self.version}.tar.bz2")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()
