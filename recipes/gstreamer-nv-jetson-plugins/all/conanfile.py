import os

from conans import *


class GstreamerNvJetsonPluginsConan(ConanFile):
    name = "gstreamer-nv-jetson-plugins"
    description = "Demo conan package"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    exports_sources = ["lib/gstreamer-1.0/*.so"]

    def requirements(self):
        self.requires("nv-jetson-drivers/[^{self.version}]")

    def package(self):
        self.copy(pattern="*.so", excludes="*libgstnvvideo4linux2.so*")
