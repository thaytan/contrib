import os
from conans import *


class BootstrapMuslConan(ConanFile):
    description = "Lightweight implementation of C standard library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("bootstrap-linux-headers/[^5.4.50]",)

    def source(self):
        tools.get(f"https://www.musl-libc.org/releases/musl-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"musl-{self.version}", ["--disable-shared"])
        autotools.install()

    def package_info(self):
        cflags = f" -idirafter {os.path.join(self.package_folder, 'include')} "

        self.env_info.CFLAGS += cflags
        self.env_info.CXXFLAGS += cflags
