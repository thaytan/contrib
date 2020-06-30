import os

from conans import *


class RustfmtConan(ConanFile):
    description = "A tool for formatting Rust code according to style guidelines"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/rust-lang/rustfmt/archive/{}.tar.gz".format(self.version))
    )
    requires = (
        "rust/nightly",
        "generators/[^1.0.0]",
    )

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rustfmt", dst="bin", keep_path=False)
