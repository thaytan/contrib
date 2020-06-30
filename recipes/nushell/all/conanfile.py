import os

from conans import ConanFile, tools


class NushellConan(ConanFile):
    name = "nushell"
    description = "Development and debugging tools for GStreamer"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        tools.get("https://github.com/nushell/nushell/archive/{}.tar.gz".format(self.version))

    def build_requirements(self):
        self.build_requires("rust/[>=1.43.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/nu", dst="bin", keep_path=False)