from conans import *
import os


class LldConan(ConanFile):
    name = "lld"
    description = "Linker from the LLVM project"
    license = "Apache 2.0"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = (
        "cmake-bootstrap/[^3.17.3]",
        "ninja-bootstrap/[^1.10.0]",
    )
    requires = (
        "generators/[^1.0.0]",
        "llvm/[^10.0.0]",
        # Prioritize llvm > llvm-bootstrap (build_requires are added firsts)
        ("llvm-bootstrap/[^10.0.0]", "private"),
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/lld-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_INSTALL_TOOLCHAIN_ONLY"] = True
        env = {
            "CPLUS_INCLUDE_PATH": "",  # Use only llvm-bootstrap header files to avoid header conflicts with libcxx
        }
        with tools.environment_append(env):
            cmake.configure(source_folder=f"{self.name}-{self.version}.src")
            cmake.build()
            cmake.install()
