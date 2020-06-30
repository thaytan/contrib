import os

from conans import *


class RacerConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/racer-rust/racer/archive/{}.tar.gz".format(self.version))

    def requirements(self):
        self.requires("rust/nightly")
        self.requires("generators/[^1.0.0]")

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/racer", dst="bin", keep_path=False)
