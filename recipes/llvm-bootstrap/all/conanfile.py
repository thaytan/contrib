import os
import shutil
from conans import *


class LlvmBootstrapConan(ConanFile):
    name = "llvm-bootstrap"
    description = "Collection of modular and reusable compiler and toolchain technologies"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = ("cmake-bootstrap/[^3.17.3]",)
    requires = (("generators/[^1.0.0]", "private"),)

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
        cmake = CMake(self, build_type="Release")

        # Reduce memory footprint of linking with gold linker
        cmake.definitions["LLVM_USE_LINKER"] = "gold"

        # LLVM build options
        if self.settings.arch_build == "x86_64":
            cmake.definitions["LLVM_TARGETS_TO_BUILD"] = "X86"
        elif self.settings.arch_build == "armv8":
            cmake.definitions["LLVM_TARGETS_TO_BUILD"] = "AArch64"
        cmake.definitions["LLVM_BUILD_RUNTIME"] = True
        cmake.definitions["LLVM_BUILD_DOCS"] = False
        cmake.definitions["LLVM_BUILD_EXAMPLES"] = False
        cmake.definitions["LLVM_BUILD_TESTS"] = False

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_ZLIB"] = True
        cmake.definitions["LLVM_ENABLE_Z3_SOLVER"] = False
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = False
        cmake.definitions["LLVM_ENABLE_FFI"] = False
        cmake.definitions["LLVM_ENABLE_LIBXML2"] = False
        cmake.definitions["LLVM_ENABLE_SPHINX"] = False

        # LLVM other options
        cmake.definitions["LLVM_INCLUDE_EXAMPLES"] = False
        cmake.definitions["LLVM_INSTALL_BINUTILS_SYMLINKS"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True

        # clang options
        cmake.definitions["CLANG_VENDOR"] = "Aivero"
        cmake.definitions["CLANG_DEFAULT_CXX_STDLIB"] = "libc++"
        cmake.definitions["CLANG_DEFAULT_LINKER"] = "lld"
        cmake.definitions["CLANG_DEFAULT_UNWINDLIB"] = "libunwind"
        cmake.definitions["CLANG_DEFAULT_RTLIB"] = "compiler-rt"
        cmake.definitions["CLANG_DEFAULT_OBJCOPY"] = "llvm-objcopy"
        cmake.definitions["CLANG_ENABLE_STATIC_ANALYZER"] = True
        cmake.definitions["LIBCLANG_BUILD_STATIC"] = True
        cmake.definitions["CLANG_BUILD_TOOLS"] = False

        # compiler-rt options
        cmake.definitions["COMPILER_RT_BUILD_SANITIZERS"] = False
        cmake.definitions["COMPILER_RT_BUILD_XRAY"] = False
        cmake.definitions["COMPILER_RT_BUILD_LIBFUZZER"] = False

        # libcxx options
        cmake.definitions["LIBCXX_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXX_ENABLE_STATIC_ABI_LIBRARY"] = True

        # libcxxabi options
        cmake.definitions["LIBCXXABI_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXXABI_USE_LLVM_UNWINDER"] = True

        # libunwind options
        cmake.definitions["LIBUNWIND_ENABLE_STATIC"] = False

        # Stage 0 build (lld, clang)
        cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage0-{self.version}")
        cmake.build(target="install-lld")
        cmake.build(target="install-clang")
        cmake.build(target="install-clang-resource-headers")
        cmake.build(target="install-libcxx")
        cmake.build(target="install-unwind")
        cmake.build(target="install-compiler-rt")

        # Use stage 0 lld and clang
        cmake.definitions["LLVM_USE_LINKER"] = os.path.join(self.package_folder, "bin", "ld.lld")
        cmake.definitions["CMAKE_C_COMPILER"] = os.path.join(self.package_folder, "bin", "clang")
        cmake.definitions["CMAKE_CXX_COMPILER"] = os.path.join(self.package_folder, "bin", "clang++")

        # Stage0 clang can actually create useful LTO libraries
        cmake.definitions["LLVM_ENABLE_LTO"] = True

        # Reduce memory usage (Needed for LTO)
        cmake.definitions["CMAKE_JOB_POOL_LINK"] = "link"
        cmake.definitions["CMAKE_JOB_POOLS"] = "link=1"

        # Stage 1 build (libcxx, libcxxabi, libunwind)
        cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage1-{self.version}")
        cmake.build(target="install-libcxx")
        cmake.build(target="install-unwind")
        cmake.build(target="install-compiler-rt")

        # Stage 2 build (whole llvm)
        env = {
            "LD_LIBRARY_PATH": os.path.join(self.package_folder, "lib"),
        }
        with tools.environment_append(env):
            cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage2-{self.version}")
            cmake.build()
            cmake.install()

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "clang")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "clang++")
        self.env_info.CFLAGS = "-flto -nostdinc"
        self.env_info.CXXFLAGS = "-flto -nostdinc -nostdinc++"
        self.env_info.LDFLAGS = "-flto"
