import os

from conans import *


class GstreamerNvJetsonPluginsConan(ConanFile):
    description = "Demo conan package"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    exports_sources = ["lib/gstreamer-1.0/*.so"]

    def requirements(self):
        self.requires("nv-jetson-drivers/[^{self.version}]")

    def package(self):
        self.copy(pattern="*.so", excludes="*libgstnvvideo4linux2.so*")
