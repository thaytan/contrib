import os
import shutil
from conans import *


class LibcxxConan(ConanFile):
    description = "LLVM C++ Standard Library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "bootstrap-cmake/[^3.18.0]",
        "bootstrap-ninja/[^1.10.0]",
        "python/[^3.8.5]",
        "libunwind/[^10.0.1]",
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
        cmake = CMake(self)

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_ENABLE_LTO"] = True

        # libcxx options
        cmake.definitions["LIBCXX_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXX_ENABLE_STATIC_ABI_LIBRARY"] = True
        cmake.definitions["LIBCXX_USE_COMPILER_RT"] = True
        if self.settings.libc_build == "musl":
            cmake.definitions["LIBCXX_HAS_MUSL_LIBC"] = True

        # libcxxabi options
        cmake.definitions["LIBCXXABI_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXXABI_USE_LLVM_UNWINDER"] = True
        cmake.definitions["LIBCXXABI_USE_COMPILER_RT"] = True
        if self.settings.libc_build == "musl":
            cmake.definitions["LIBCXXABI_ENABLE_STATIC_UNWINDER"] = True

        env = {"CXXFLAGS": ""}
        with tools.environment_append(env):
            cmake.configure(source_folder=f"llvm-{self.version}")
            cmake.build(target="install-libcxx")
