import os

from conans import ConanFile, tools


class RlsConan(ConanFile):
    name = "rls"
    version = tools.get_env("GIT_TAG", "master")
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = "os", "arch", "compiler"

    def source(self):
        tools.get("https://github.com/rust-lang/rls/archive/{}.tar.gz".format(self.version))

    def requirements(self):
        self.requires("rust/nightly@%s/stable" % self.user)
        self.requires("openssl/1.1.1b@%s/stable" % self.user)
        self.requires("generators/[>=1.0.0]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rls", dst="bin", keep_path=False)
