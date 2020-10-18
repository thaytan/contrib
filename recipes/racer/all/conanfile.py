import os

from conans import *


class RacerConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

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
