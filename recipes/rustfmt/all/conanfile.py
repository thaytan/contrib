import os

from conans import *


class RustfmtConan(ConanFile):
    description = "A tool for formatting Rust code according to style guidelines"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/rust-lang/rustfmt/archive/{self.version}.tar.gz")
    )
    requires = (
        "generators/[^1.0.0]",
        "rust/nightly",
        "generators/[^1.0.0]",
    )

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rustfmt", dst="bin", keep_path=False)
