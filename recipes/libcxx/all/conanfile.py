import os
import shutil
from conans import *


class LibcxxConan(ConanFile):
    name = "libcxx"
    description = "LLVM C++ Standard Library"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = (
        "clang-bootstrap/[^10.0.0]",
        "cmake-bootstrap/[^3.17.3]",
        "ninja-bootstrap/[^1.10.0]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxx-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxxabi-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libunwind-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        shutil.move(f"libcxx-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxx"))
        shutil.move(f"libcxxabi-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxxabi"))
        shutil.move(f"libunwind-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libunwind"))

    def build(self):
        cmake = CMake(self, generator="Ninja")

        # LLVM build options
        cmake.definitions["LLVM_BUILD_DOCS"] = False
        cmake.definitions["LLVM_BUILD_EXAMPLES"] = False
        cmake.definitions["LLVM_BUILD_RUNTIME"] = True
        cmake.definitions["LLVM_BUILD_TESTS"] = False

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_ASSERTIONS"] = False
        cmake.definitions["LLVM_ENABLE_FFI"] = False
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_ENABLE_PIC"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_SPHINX"] = False
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = True
        cmake.definitions["LLVM_ENABLE_ZLIB"] = True
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"] = False

        # libcxxabi options
        cmake.definitions["LIBCXXABI_USE_LLVM_UNWINDER"] = True

        # No static libs
        cmake.definitions["LIBCXX_ENABLE_STATIC"] = False
        cmake.definitions["LIBCXXABI_ENABLE_STATIC"] = False
        cmake.definitions["LIBCXXABI_LINK_TESTS_WITH_SHARED_LIBCXX"] = True
        cmake.definitions["LIBUNWIND_ENABLE_STATIC"] = False

        cmake.configure(source_folder=f"llvm-{self.version}")
        cmake.build(target="cxx")
        cmake.build(target="install-libcxx")
        cmake.build(target="install-libcxxabi")
        cmake.build(target="install-unwind")
