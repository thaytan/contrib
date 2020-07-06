import os

from conans import *


class NushellConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/nushell/nushell/archive/{self.version}.tar.gz")

    build_requires = ("rust/[^1.43.1]",)
    requires = (
        "base/[^1.0.0]",
        "openssl/[^1.1.1b]",
    )

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/nu", dst="bin", keep_path=False)
