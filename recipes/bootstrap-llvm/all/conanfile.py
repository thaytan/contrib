import os
import shutil
from conans import *


class BootstrapLlvmConan(ConanFile):
    musl_version = "1.2.0"
    description = "Collection of modular and reusable compiler and toolchain technologies"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("bootstrap-cmake/[^3.18.0]", "bootstrap-ninja/[^1.10.0]")
    requires = "bootstrap-libc/[^1.0.0]"

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/lld-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxx-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxxabi-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        shutil.move(f"clang-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "clang"))
        shutil.move(f"lld-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "lld"))
        shutil.move(f"libcxx-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxx"))
        shutil.move(f"libcxxabi-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxxabi"))

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
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-musl-headers"].rootpath, "include")
            abi = "musl"
        else:
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-glibc-headers"].rootpath, "include")
            abi = "gnu"
        cmake.definitions["LLVM_HOST_TRIPLE"] = f"{arch}-aivero-linux-{abi}"

        cmake.definitions["LLVM_ENABLE_PIC"] = True
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
        cmake.definitions["CLANG_DEFAULT_LINKER"] = "lld"
        cmake.definitions["CLANG_DEFAULT_OBJCOPY"] = "llvm-objcopy"
        cmake.definitions["CLANG_DEFAULT_CXX_STDLIB"] = "libc++"
        cmake.definitions["CLANG_ENABLE_STATIC_ANALYZER"] = True
        cmake.definitions["LIBCLANG_BUILD_STATIC"] = True

        # libcxx options
        cmake.definitions["LIBCXX_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXX_ENABLE_STATIC_ABI_LIBRARY"] = True
        if self.settings.libc_build == "musl":
            cmake.definitions["LIBCXX_HAS_MUSL_LIBC"] = True

        # libcxxabi options
        cmake.definitions["LIBCXXABI_ENABLE_SHARED"] = False

        ###########
        # Stage 0 #
        ###########

        # Install stage 0 to build directory
        stage0_folder = os.path.join(self.build_folder, f"stage0-{self.version}-install")
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = stage0_folder

        # Reduce memory footprint of linking with gold linker
        cmake.definitions["LLVM_USE_LINKER"] = "gold"

        # Stage 0 build (lld, clang, ar)
        cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage0-{self.version}")
        cmake.build(target="install-clang")
        cmake.build(target="install-clang-resource-headers")
        cmake.build(target="install-ar")
        cmake.build(target="install-ranlib")
        cmake.build(target="install-strip")
        cmake.build(target="install-lld")
        cmake.build(target="install-llvm-tblgen")
        cmake.build(target="install-libcxx")

        ###########
        # Stage 1 #
        ###########

        # Install stage 1 to build directory
        stage1_folder = os.path.join(self.build_folder, f"stage1-{self.version}-install")
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = stage1_folder

        # Use stage 0 lld, clang, ar and ranlib
        cmake.definitions["LLVM_USE_LINKER"] = os.path.join(stage0_folder, "bin", "ld.lld")
        cmake.definitions["CMAKE_C_COMPILER"] = os.path.join(stage0_folder, "bin", "clang")
        cmake.definitions["CMAKE_CXX_COMPILER"] = os.path.join(stage0_folder, "bin", "clang++")
        cmake.definitions["CMAKE_AR"] = os.path.join(stage0_folder, "bin", "ar")
        cmake.definitions["CMAKE_RANLIB"] = os.path.join(stage0_folder, "bin", "ranlib")
        cmake.definitions["LLVM_TABLEGEN"] = os.path.join(stage0_folder, "bin", "llvm-tblgen")

        # Stage 0 clang can actually create useful LTO libraries
        cmake.definitions["LLVM_ENABLE_LTO"] = "Thin"

        # Statically link everything with musl
        cflags = ""
        if self.settings.libc_build == "musl":
            cflags = "-static"
        env = {
            "CFLAGS": cflags,
            "CXXLAGS": cflags,
            "LDFLAGS": cflags,
        }

        # Stage 1 build (libcxx, libcxxabi)
        with tools.environment_append(env):
            cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage1-{self.version}")
            cmake.build(target="install-libcxx")

        ###########
        # Stage 2 #
        ###########

        # Install stage 2 to package directory
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder

        # Use stage 1 libs
        ldflags = ""
        # GVN causes segmentation fault during recursion higher than 290
        if self.settings.libc_build == "musl":
            ldflags = "-Wl,-mllvm,-gvn-max-recurse-depth=250"
        clang_inc = os.path.join(stage1_folder, "lib", "clang", self.version, "include")
        clang_lib = os.path.join(stage1_folder, "lib", "clang", self.version, "lib", "linux")
        libcxx_inc = os.path.join(stage1_folder, "include", "c++", "v1")
        libcxx_lib = os.path.join(stage1_folder, "lib")
        env = {
            "LD_LIBRARY_PATH": libcxx_lib,
            "CFLAGS": cflags,  # Needed for tests
            "CXXFLAGS": f"{cflags} -idirafter {libcxx_inc} -idirafter {clang_inc} -idirafter {libc_inc}",
            "LDFLAGS": f"{cflags} {ldflags} -L{clang_lib} -L{libcxx_lib}",
        }

        # Stage 2 build (lld, clang, libcxx, libcxxabi)
        with tools.environment_append(env):
            cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage2-{self.version}")
            cmake.build(target="install-libcxx")
            cmake.build(target="install-clang")
            cmake.build(target="install-clang-resource-headers")
            cmake.build(target="install-ar")
            cmake.build(target="install-ranlib")
            cmake.build(target="install-strip")
            cmake.build(target="install-objcopy")
            cmake.build(target="install-objdump")
            cmake.build(target="install-nm")
            cmake.build(target="install-lld")
            cmake.build(target="install-llvm-as")
            cmake.build(target="install-llvm-config")
            cmake.build(target="install-llvm-tblgen")
            cmake.build(target="install-llvm-profdata")
            cmake.build(target="install-FileCheck")

        # Make lld, clang, clang++ default
        with tools.chdir(os.path.join(self.package_folder, "bin")):
            os.symlink("ld.lld", "ld")
            os.symlink("clang", "cc")
            os.symlink("clang++", "c++")

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "clang")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "clang++")
        self.env_info.AR = os.path.join(self.package_folder, "bin", "ar")
        self.env_info.AS = os.path.join(self.package_folder, "bin", "llvm-as")
        self.env_info.RANLIB = os.path.join(self.package_folder, "bin", "ranlib")
        self.env_info.LD = os.path.join(self.package_folder, "bin", "ld")
        self.env_info.STRIP = os.path.join(self.package_folder, "bin", "strip")
        self.env_info.OBJCOPY = os.path.join(self.package_folder, "bin", "objcopy")

        static_flags = ""
        if self.settings.libc_build == "musl":
            static_flags = "-static"
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-musl-headers"].rootpath, "include")
        else:
            static_flags = ""
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-glibc-headers"].rootpath, "include")
        clang_inc = os.path.join(self.package_folder, "lib", "clang", self.version, "include")
        libcxx_inc = os.path.join(self.package_folder, "include", "c++", "v1")
        cflags = f" -nostdinc -idirafter {clang_inc} -idirafter {libc_inc} {static_flags} -fPIC -flto=thin -nostdinc "
        cxxflags = f" -nostdinc++ -idirafter {libcxx_inc} {cflags} "

        self.env_info.CFLAGS = cflags
        self.env_info.CXXFLAGS = cxxflags
