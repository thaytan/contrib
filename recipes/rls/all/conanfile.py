import os

from conans import ConanFile, tools


class RlsConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/rust-lang/rls/archive/{}.tar.gz".format(self.version))

    def requirements(self):
        self.requires("rust/nightly")
        self.requires("openssl/1.1.1b")
        self.requires("generators/[^1.0.0]")

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rls", dst="bin", keep_path=False)
