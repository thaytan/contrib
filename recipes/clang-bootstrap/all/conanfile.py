import os
import shutil
from conans import *


class ClangBootstrapConan(ConanFile):
    name = "clang-bootstrap"
    description = "C language family frontend for LLVM"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cmake-bootstrap/[^3.17.3]",
        "ninja-bootstrap/[^1.10.0]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/lld-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        shutil.move(f"clang-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "clang"))
        shutil.move(f"lld-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "lld"))

    def build(self):
        cmake = CMake(self, generator="Ninja", build_type="Release")

        # Reduce memory footprint of linking with gold linker
        cmake.definitions["LLVM_USE_LINKER"] = "gold"

        cmake.definitions["LLVM_BUILD_DOCS"] = False
        cmake.definitions["LLVM_BUILD_EXAMPLES"] = False
        cmake.definitions["LLVM_BUILD_RUNTIME"] = False
        cmake.definitions["LLVM_BUILD_TESTS"] = False

        cmake.definitions["LLVM_ENABLE_ASSERTIONS"] = False
        cmake.definitions["LLVM_ENABLE_FFI"] = False
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = False
        cmake.definitions["LLVM_ENABLE_PIC"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_SPHINX"] = False
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = False
        cmake.definitions["LLVM_ENABLE_ZLIB"] = True

        cmake.definitions["LLVM_INCLUDE_EXAMPLES"] = False

        cmake.configure(source_folder=f"llvm-{self.version}")
        cmake.build(target="lld")
        cmake.build(target="install-lld")
        cmake.build(target="clang")
        cmake.build(target="install-clang")
        cmake.build(target="install-clang-resource-headers")

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "clang")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "clang++")
