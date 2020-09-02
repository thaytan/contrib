import os

from conans import *


class BootstrapMuslConan(ConanFile):
    name = "bootstrap-musl"
    description = "Lightweight implementation of C standard library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build"
    requires = (("generators/[^1.0.0]", "private"),)

    def source(self):
        tools.get(f"https://www.musl-libc.org/releases/musl-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"musl-{self.version}")
        autotools.make(target="install-headers")
