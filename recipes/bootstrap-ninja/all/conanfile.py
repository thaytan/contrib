import os

from conans import *


class BootstrapNinjaConan(ConanFile):
    name = "bootstrap-ninja"
    description = "Small build system with a focus on speed"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("bootstrap-libc-headers/[^1.0.0]", "bootstrap-cmake/[^3.18.0]")
    requires = (("generators/[^1.0.0]", "private"),)

    def source(self):
        tools.get(f"https://github.com/ninja-build/ninja/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_USE_OPENSSL"] = False
        cmake.configure(source_folder=f"ninja-{self.version}")
        cmake.build()

    def package(self):
        self.copy("ninja", "bin")

    def package_info(self):
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
