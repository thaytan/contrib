import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class XzConan(ConanFile):
    description = "Library and command line tools for XZ and LZMA compressed files"
    license = "custom", "GPL", "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://tukaani.org/xz/xz-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
