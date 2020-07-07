from conans import *
import os


class ClangBootstrapConan(ConanFile):
    name = "clang-bootstrap"
    description = "C language family frontend for LLVM"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cmake-bootstrap/[^3.17.3]",
        "ninja-bootstrap/[^1.10.0]",
        "libunwind-bootstrap/[^1.3.1]",
    )
    requires = ("llvm-bootstrap/[^10.0.0]",)

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.configure(source_folder=f"clang-{self.version}.src")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "clang")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "clang++")
