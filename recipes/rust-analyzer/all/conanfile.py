import os

from conans import ConanFile, tools


class RustAnalyzerConan(ConanFile):
    description = "An experimental Rust compiler front-end for IDEs."
    license = "MIT", "Apache2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/rust-analyzer/rust-analyzer/archive/{}.tar.gz".format(self.version.replace(".", "-")))

    def requirements(self):
        self.requires("rust/nightly@%s/stable" % self.user)
        self.requires("generators/[^1.0.0]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rust-analyzer", dst="bin", keep_path=False)
