import os
import shutil
from conans import *


class CompilerRtConan(ConanFile):
    name = "compiler-rt"
    description = "Compiler runtime libraries for clang"
    license = "Apache 2.0"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = (
        "llvm/[^10.0.0]",
        "llvm-bootstrap/[^10.0.0]",
        "cmake-bootstrap/[^3.17.3]",
        "ninja-bootstrap/[^1.10.0]",
        "linux-headers/[^5.4.50]",
    )
    requires = (("generators/[^1.0.0]", "private"),)

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/compiler-rt-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["COMPILER_RT_BUILD_SANITIZERS"] = False
        cmake.definitions["COMPILER_RT_BUILD_XRAY"] = False
        cmake.definitions["COMPILER_RT_BUILD_LIBFUZZER"] = False
        cmake.definitions["COMPILER_RT_INCLUDE_TESTS"] = False
        env = {
            "CPLUS_INCLUDE_PATH": "",  # Use only llvm-bootstrap header files to avoid header conflicts with libcxx
        }
        with tools.environment_append(env):
            cmake.configure(source_folder=f"compiler-rt-{self.version}.src")
            cmake.build()
            cmake.install()
