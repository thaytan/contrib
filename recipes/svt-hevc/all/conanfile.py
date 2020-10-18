import os

from conans import *


class SvtHevcConan(ConanFile):
    description = "The Scalable Video Technology for HEVC Encoder"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
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
