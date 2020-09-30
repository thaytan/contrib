import os
import shutil
from conans import *


class LibunwindConan(ConanFile):
    description = "LLVM libunwind"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "bootstrap-cmake/[^3.18.0]",
        "bootstrap-ninja/[^1.10.0]",
        "python/[^3.8.5]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libunwind-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        shutil.move(f"libunwind-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libunwind"))

    def build(self):
        cmake = CMake(self)

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_LTO"] = True

        # libunwind options
        cmake.definitions["LIBUNWIND_USE_COMPILER_RT"] = True
        cmake.definitions["LIBUNWIND_ENABLE_SHARED"] = True
        cmake.definitions["LIBUNWIND_ENABLE_STATIC"] = False

        cmake.configure(source_folder=f"llvm-{self.version}")
        cmake.build(target="install-unwind")
