import os
from conans import *


class BootstrapCMakeConan(ConanFile):
    name = "bootstrap-cmake"
    description = "A cross-platform open-source make system + ninja"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("bootstrap-libc-headers/[^1.0.0]",)

    def source(self):
        tools.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_USE_OPENSSL"] = False
        cmake.configure(source_folder=f"cmake-{self.version}")
        cmake.build()
        cmake.install()
