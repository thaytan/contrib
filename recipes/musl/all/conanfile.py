from conans import *


class MuslConan(ConanFile):
    description = "Lightweight implementation of C standard library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("linux-headers/[^5.4.50]",)

    def source(self):
        tools.get(f"https://www.musl-libc.org/releases/musl-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"musl-{self.version}", ["--disable-shared"])
        autotools.install()
