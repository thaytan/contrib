import os

from conans import *


class RacerConan(ConanFile):
    name = "racer"
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/racer-rust/racer/archive/{self.version}.tar.gz")
    )
    requires = (
        "base/[^1.0.0]",
        "rust/nightly",
        "base/[^1.0.0]",
    )

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/racer", dst="bin", keep_path=False)
