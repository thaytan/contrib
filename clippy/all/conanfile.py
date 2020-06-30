import os

from conans import ConanFile, tools


class ClippyConan(ConanFile):
    name = "clippy"
    version = tools.get_env("GIT_TAG", "master")
    description = "A bunch of lints to catch common mistakes and improve your Rust code"
    license = "Apache2"
    settings = "os", "arch", "compiler"

    def source(self):
        tools.get("https://github.com/rust-lang/rust-clippy/archive/%s.tar.gz" % self.version)

    def build_requirements(self):
        self.build_requires("rust/nightly@%s/stable" % self.user)

    def requirements(self):
        self.requires("generators/[>=1.0.0]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("rust-clippy-%s" % self.version):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/cargo-clippy", dst="bin", keep_path=False)
        self.copy(pattern="*/clippy-driver", dst="bin", keep_path=False)
