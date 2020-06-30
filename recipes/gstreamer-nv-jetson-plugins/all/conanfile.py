import os

from conans import *


class GstreamerNvJetsonPluginsConan(ConanFile):
    description = "Demo conan package"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports_sources = ["lib/gstreamer-1.0/*.so"]
    build_requires = (
        "generators/1.0.0",
    )
    requires = (
        "nv-jetson-drivers/[^%s]" % (self.version),

    def package(self):
        self.copy(pattern="*.so", excludes="*libgstnvvideo4linux2.so*")
