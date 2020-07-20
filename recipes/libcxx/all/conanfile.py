import os
import shutil
from conans import *


class LibcxxConan(ConanFile):
    name = "libcxx"
    description = "LLVM C++ Standard Library"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = (
        "llvm-bootstrap/[^10.0.0]",
        "cmake-bootstrap/[^3.17.3]",
    )
    requires = (("generators/[^1.0.0]", "private"),)

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
        cmake = CMake(self)

        # LLVM build options
        cmake.definitions["LLVM_BUILD_DOCS"] = False
        cmake.definitions["LLVM_BUILD_EXAMPLES"] = False
        cmake.definitions["LLVM_BUILD_RUNTIME"] = True
        cmake.definitions["LLVM_BUILD_TESTS"] = False

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_LTO"] = True
        cmake.definitions["LLVM_ENABLE_ASSERTIONS"] = False
        cmake.definitions["LLVM_ENABLE_FFI"] = False
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_ENABLE_PIC"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_SPHINX"] = False
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = True
        cmake.definitions["LLVM_ENABLE_ZLIB"] = True
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"] = False
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True

        # libcxx options
        cmake.definitions["LIBCXX_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXX_ENABLE_STATIC_ABI_LIBRARY"] = True
        cmake.definitions["LIBCXX_USE_COMPILER_RT"] = True

        # libcxxabi options
        cmake.definitions["LIBCXXABI_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXXABI_ENABLE_STATIC_UNWINDER"] = True
        cmake.definitions["LIBCXXABI_USE_LLVM_UNWINDER"] = True
        cmake.definitions["LIBCXXABI_USE_COMPILER_RT"] = True

        # libunwind options
        cmake.definitions["LIBUNWIND_ENABLE_SHARED"] = True

        cmake.configure(source_folder=f"llvm-{self.version}")
        cmake.build(target="install-libcxx")
        cmake.build(target="install-unwind")

    def package_info(self):
        self.env_info.CPLUS_INCLUDE_PATH = os.path.join(self.package_folder, "include", "c++", "v1")
