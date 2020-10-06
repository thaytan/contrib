import shutil
from conans import *


class LlvmConan(ConanFile):
    description = "Collection of modular and reusable compiler and toolchain technologies"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "bootstrap-cmake/[^3.18.0]",
        "bootstrap-ninja/[^1.10.0]",
        "python/[^3.8.5]",
        "zlib/[^1.2.11]",
        "ncurses/[^6.2]",
        "libffi/[^3.3]",
    )
    requires = ("libcxx/[^10.0.1]",)

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")

    def build(self):
        cmake = CMake(self)

        # LLVM build options
        if self.settings.arch_build == "x86_64":
            cmake.definitions["LLVM_TARGETS_TO_BUILD"] = "X86"
            arch = "x86_64"
        elif self.settings.arch_build == "armv8":
            cmake.definitions["LLVM_TARGETS_TO_BUILD"] = "AArch64"
            arch = "aarch64"
        if self.settings.libc_build == "musl":
            abi = "musl"
        else:
            abi = "gnu"
        cmake.definitions["LLVM_HOST_TRIPLE"] = f"{arch}-aivero-linux-{abi}"

        cmake.definitions["LLVM_BUILD_RUNTIME"] = True
        cmake.definitions["LLVM_BUILD_DOCS"] = False
        cmake.definitions["LLVM_BUILD_EXAMPLES"] = False
        cmake.definitions["LLVM_BUILD_TESTS"] = False

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_LTO"] = True
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_PIC"] = True
        cmake.definitions["LLVM_ENABLE_ZLIB"] = True
        cmake.definitions["LLVM_ENABLE_FFI"] = True
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = True
        cmake.definitions["LLVM_ENABLE_Z3_SOLVER"] = False
        cmake.definitions["LLVM_ENABLE_SPHINX"] = False
        cmake.definitions["LLVM_ENABLE_LIBXML2"] = False

        # LLVM other options
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"] = False

        cmake.configure(source_folder=f"llvm-{self.version}")
        cmake.build()
        cmake.install()
