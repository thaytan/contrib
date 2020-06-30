import os

from conans import *


class ClippyConan(ConanFile):
    description = "A bunch of lints to catch common mistakes and improve your Rust code"
    license = "Apache2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/rust-lang/rust-clippy/archive/%s.tar.gz" % self.version)

    build_requires = ("rust/nightly",)
    requires = ("generators/[^1.0.0]",)

    def build(self):
        with tools.chdir("rust-clippy-%s" % self.version):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/cargo-clippy", dst="bin", keep_path=False)
        self.copy(pattern="*/clippy-driver", dst="bin", keep_path=False)
