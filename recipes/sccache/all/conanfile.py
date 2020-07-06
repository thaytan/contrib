import os

from conans import *


class SccacheConan(ConanFile):
    name = "sccache"
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/mozilla/sccache/archive/{self.version}.tar.gz")

    build_requires = (
        "base/[^1.0.0]",
        "rust/[^1.3.8]",
        "openssl/[^1.1.1b]",
    )

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/sccache", dst="bin", keep_path=False)

    def package_info(self):
        self.env_info.RUSTC_WRAPPER = "sccache"
