import os

from conans import *


class SvtHevcConan(ConanFile):
    description = "The Scalable Video Technology for HEVC Encoder"
    license = "BSD"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("cmake/[^3.15.3]")
        self.build_requires("yasm/[^1.3.0]")

    def source(self):
        tools.get("https://github.com/OpenVisualCloud/SVT-HEVC/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="SVT-HEVC-%s" % self.version)
        cmake.build()
        cmake.install()
