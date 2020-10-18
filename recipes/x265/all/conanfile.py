import os

from conans import *


class X265Conan(ConanFile):
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"bit_depth": [8, 10, 12], "HDR10": [True, False]}
    default_options = "bit_depth=8", "HDR10=False"
    build_requires = (
        "cmake/[^3.15.3]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        tools.get(f"https://github.com/videolan/x265/archive/{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["HIGH_BIT_DEPTH"] = self.options.bit_depth != 8
        cmake.definitions["MAIN12"] = self.options.bit_depth == 12
        cmake.definitions["ENABLE_HDR10_PLUS"] = self.options.HDR10
        cmake.configure(source_folder=os.path.join(f"{self.name, self.version)}-{"source"}")
        cmake.install()
