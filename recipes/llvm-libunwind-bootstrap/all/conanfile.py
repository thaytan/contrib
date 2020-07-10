from conans import *


class LibunwindBoostrapConan(ConanFile):
    name = "libunwind-bootstrap"
    description = "LLVM version of libunwind library"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libunwind-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"libunwind-{self.version}.src")
        cmake.build()
        cmake.install()
