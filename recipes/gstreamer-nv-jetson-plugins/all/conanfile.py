import os

from conans import ConanFile, tools


class GstreamerNvJetsonPluginsConan(ConanFile):
    description = "Demo conan package"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports_sources = ["lib/gstreamer-1.0/*.so"]

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def requirements(self):
        self.requires("nv-jetson-drivers/[>=%s]@%s/stable" % (self.version, self.user))

    def package(self):
        self.copy(pattern="*.so", excludes="*libgstnvvideo4linux2.so*")
