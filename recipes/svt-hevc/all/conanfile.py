import os

from conans import *


class SvtHevcConan(ConanFile):
    description = "The Scalable Video Technology for HEVC Encoder"
    license = "BSD"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cmake/[^3.15.3]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        tools.get(f"https://github.com/OpenVisualCloud/SVT-HEVC/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"SVT-HEVC-{self.version}")
        cmake.build()
        cmake.install()
