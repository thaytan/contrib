import os

from conans import *


class SccacheConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

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
