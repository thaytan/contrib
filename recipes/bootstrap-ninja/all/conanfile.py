import os

from conans import *


class BootstrapNinjaConan(ConanFile):
    name = "ninja"
    description = "Small build system with a focus on speed"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system", "musl"]}
    build_requires = ("bootstrap-cmake/[^3.18.0]",)

    def source(self):
        tools.get(f"https://github.com/ninja-build/ninja/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_USE_OPENSSL"] = False
        cmake.configure(source_folder=f"ninja-{self.version}")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
