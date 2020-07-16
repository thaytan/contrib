import os
import shutil
from conans import *


class LlvmBootstrapConan(ConanFile):
    name = "llvm-bootstrap"
    description = "Collection of modular and reusable compiler and toolchain technologies"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = ("cmake-bootstrap/[^3.17.3]",)

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/lld-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/compiler-rt-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxx-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxxabi-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libunwind-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        shutil.move(f"clang-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "clang"))
        shutil.move(f"lld-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "lld"))
        shutil.move(f"compiler-rt-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "compiler-rt"))
        shutil.move(f"libcxx-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxx"))
        shutil.move(f"libcxxabi-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxxabi"))
        shutil.move(f"libunwind-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libunwind"))

    def build(self):
        cmake = CMake(self, generator="Ninja", build_type="Release")

        # Reduce memory footprint of linking with gold linker
        cmake.definitions["LLVM_USE_LINKER"] = "gold"

        # LLVM build options
        cmake.definitions["LLVM_BUILD_DOCS"] = False
        cmake.definitions["LLVM_BUILD_EXAMPLES"] = False
        cmake.definitions["LLVM_BUILD_RUNTIME"] = True
        cmake.definitions["LLVM_BUILD_TESTS"] = False

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_ASSERTIONS"] = False
        cmake.definitions["LLVM_ENABLE_FFI"] = False
        cmake.definitions["LLVM_ENABLE_LIBXML2"] = False
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_ENABLE_PIC"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_SPHINX"] = False
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = True
        cmake.definitions["LLVM_ENABLE_ZLIB"] = True

        # LLVM other options
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"] = False
        cmake.definitions["LLVM_INSTALL_BINUTILS_SYMLINKS"] = True

        # clang options
        cmake.definitions["CLANG_DEFAULT_CXX_STDLIB"] = "libc++"
        cmake.definitions["CLANG_DEFAULT_LINKER"] = "lld"
        cmake.definitions["CLANG_DEFAULT_UNWINDLIB"] = "libunwind"
        cmake.definitions["CLANG_DEFAULT_RTLIB"] = "compiler-rt"

        # compiler-rt options
        cmake.definitions["COMPILER_RT_BUILD_SANITIZERS"] = False
        cmake.definitions["COMPILER_RT_BUILD_XRAY"] = False
        cmake.definitions["COMPILER_RT_BUILD_LIBFUZZER"] = False

        # libcxxabi options
        cmake.definitions["LIBCXXABI_USE_LLVM_UNWINDER"] = True

        # No static libs
        cmake.definitions["LIBCXX_ENABLE_STATIC"] = False
        cmake.definitions["LIBCXXABI_ENABLE_STATIC"] = False
        cmake.definitions["LIBCXXABI_LINK_TESTS_WITH_SHARED_LIBCXX"] = True
        cmake.definitions["LIBUNWIND_ENABLE_STATIC"] = False

        cmake.configure(source_folder=f"llvm-{self.version}")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "clang")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "clang++")
