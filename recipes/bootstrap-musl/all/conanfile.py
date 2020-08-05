import os

from conans import *


class BootstrapMuslConan(ConanFile):
    name = "bootstrap-musl"
    description = "Lightweight implementation of C standard library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["musl"]}

    def source(self):
        tools.get(f"https://www.musl-libc.org/releases/musl-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"musl-{self.version}")
        autotools.make(target="install-headers")
