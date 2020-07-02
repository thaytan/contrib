import os

from conans import *


class RlsConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/rust-lang/rls/archive/{self.version}.tar.gz")
    )
    requires = (
        "generators/[^1.0.0]",
        "rust/nightly",
        "openssl/1.1.1b",
        "generators/[^1.0.0]",
    )

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rls", dst="bin", keep_path=False)
