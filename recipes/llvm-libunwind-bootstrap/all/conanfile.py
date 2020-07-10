from conans import *


class LlvmLibunwindBoostrapConan(ConanFile):
    name = "llvm-libunwind-bootstrap"
    description = "LLVM version of libunwind library"
    license = "Apache-2.0"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cmake-bootstrap/[^3.17.3]",
        "ninja-bootstrap/[^1.10.0]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libunwind-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"libunwind-{self.version}.src")
        cmake.build()
        cmake.install()
