import os

from conans import *


class SccacheConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/mozilla/sccache/archive/{}.tar.gz".format(self.version))

    def build_requirements(self):
        self.build_requires("generators/[^1.0.0]")
        self.build_requires("rust/[^1.3.8]")
        self.build_requires("openssl/[^1.1.1b]")

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/sccache", dst="bin", keep_path=False)

    def package_info(self):
        self.env_info.RUSTC_WRAPPER = "sccache"
