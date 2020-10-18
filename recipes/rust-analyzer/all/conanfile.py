import os

from conans import *


class RustAnalyzerConan(ConanFile):
    description = "An experimental Rust compiler front-end for IDEs."
    license = "MIT", "Apache2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://github.com/rust-analyzer/rust-analyzer/archive/{self.version.replace('.', '-')}.tar.gz")

    requires = (
        "base/[^1.0.0]",
        "rust/nightly",
        "base/[^1.0.0]",
    )

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rust-analyzer", dst="bin", keep_path=False)
