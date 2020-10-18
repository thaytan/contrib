import os

from conans import *


class ClippyConan(ConanFile):
    description = "A bunch of lints to catch common mistakes and improve your Rust code"
    license = "Apache2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://github.com/rust-lang/rust-clippy/archive/{self.version}.tar.gz")

    build_requires = ("rust/nightly",)
    requires = (
        "base/[^1.0.0]",
        "base/[^1.0.0]",
    )

    def build(self):
        with tools.chdir(f"rust-clippy-{self.version}"):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/cargo-clippy", dst="bin", keep_path=False)
        self.copy(pattern="*/clippy-driver", dst="bin", keep_path=False)
