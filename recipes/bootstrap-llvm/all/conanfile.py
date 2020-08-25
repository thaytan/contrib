import os
import shutil
from conans import *


class BootstrapLlvmConan(ConanFile):
    name = "bootstrap-llvm"
    musl_version = "1.2.0"
    description = "Collection of modular and reusable compiler and toolchain technologies"
    license = "custom"
    settings = {"build_type": ["RelWithDebInfo"], "os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system", "musl"]}
    build_requires = ("bootstrap-cmake/[^3.18.0]", "bootstrap-ninja/[^1.10.0]")
    requires = (("generators/[^1.0.0]", "private"),)

    def requirements(self):
        if self.settings.os_build == "Linux":
            if self.settings.libc_build == "system":
                self.requires("bootstrap-glibc/2.27")
            if self.settings.libc_build == "musl":
                self.requires("bootstrap-musl/1.2.1")

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

        if self.settings.libc_build == "musl":
            tools.get(f"https://www.musl-libc.org/releases/musl-{self.musl_version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        # Reduce memory footprint of linking with gold linker
        cmake.definitions["LLVM_USE_LINKER"] = "gold"

        # LLVM build options
        if self.settings.arch_build == "x86_64":
            cmake.definitions["LLVM_TARGETS_TO_BUILD"] = "X86"
            arch = "x86_64"
        elif self.settings.arch_build == "armv8":
            cmake.definitions["LLVM_TARGETS_TO_BUILD"] = "AArch64"
            arch = "aarch64"
        if self.settings.libc_build == "musl":
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-musl"].rootpath, "include")
            abi = "musl"
        else:
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-glibc"].rootpath, "include")
            abi = "gnu"
        cmake.definitions["LLVM_HOST_TRIPLE"] = f"{arch}-aivero-linux-{abi}"

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

        # compiler-rt options
        cmake.definitions["COMPILER_RT_BUILD_SANITIZERS"] = False
        cmake.definitions["COMPILER_RT_BUILD_XRAY"] = False
        cmake.definitions["COMPILER_RT_BUILD_LIBFUZZER"] = False

        # libcxx options
        cmake.definitions["LIBCXX_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXX_ENABLE_STATIC_ABI_LIBRARY"] = True
        if self.settings.libc_build == "musl":
            cmake.definitions["LIBCXX_HAS_MUSL_LIBC"] = True

        # libcxxabi options
        cmake.definitions["LIBCXXABI_ENABLE_SHARED"] = False
        cmake.definitions["LIBCXXABI_USE_LLVM_UNWINDER"] = True
        cmake.definitions["LIBCXXABI_ENABLE_STATIC_UNWINDER"] = True

        # libunwind options
        cmake.definitions["LIBUNWIND_ENABLE_SHARED"] = False

        # Stage 0 build (lld, clang, ar, libcxx)
        cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage0-{self.version}")
        cmake.build(target="install-clang")
        cmake.build(target="install-clang-resource-headers")
        cmake.build(target="install-ar")
        cmake.build(target="install-ranlib")
        cmake.build(target="install-lld")
        cmake.build(target="install-libcxx")
        cmake.build(target="install-unwind")
        cmake.build(target="install-compiler-rt")
        cmake.build(target="install-llvm-tblgen")

        # Use stage 0 lld, clang, ar and ranlib
        cmake.definitions["LLVM_USE_LINKER"] = os.path.join(self.package_folder, "bin", "ld.lld")
        cmake.definitions["CMAKE_C_COMPILER"] = os.path.join(self.package_folder, "bin", "clang")
        cmake.definitions["CMAKE_CXX_COMPILER"] = os.path.join(self.package_folder, "bin", "clang++")
        cmake.definitions["CMAKE_AR"] = os.path.join(self.package_folder, "bin", "ar")
        cmake.definitions["CMAKE_RANLIB"] = os.path.join(self.package_folder, "bin", "ranlib")
        cmake.definitions["LLVM_TABLEGEN"] = os.path.join(self.package_folder, "bin", "llvm-tblgen")

        # Stage0 clang can actually create useful LTO libraries
        cmake.definitions["LLVM_ENABLE_LTO"] = "Thin"

        # Build musl
        ldflags = "-static-libgcc"
        if self.settings.libc_build == "musl":
            env = {
                "LD_LIBRARY_PATH": os.path.join(self.package_folder, "lib"),
                "CC": os.path.join(self.package_folder, "bin", "clang"),
                "CFLAGS": f"-nostdinc -isystem {os.path.join(self.package_folder, 'include')} -L{os.path.join(self.package_folder, 'lib', 'clang', self.version, 'lib', 'linux')}",
                "LDFLAGS": f"-L{os.path.join(self.package_folder, 'lib', 'clang', self.version, 'lib', 'linux')}",
                "TARGET": f"{arch}-linux-musl",
                # "LIBRART_PATH": "/usr/lib/llvm-10/lib/clang/10.0.0/lib/linux",
                "LIBCC": f"-lclang_rt.builtins-{arch}",
            }
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(vars=env, configure_dir=f"musl-{self.musl_version}")
            autotools.make(target="install-libs", args=['CFLAGS_AUTO=" -O2 -pipe"'])
            # GVN causes segmentation fault during recursion higher than 290
            ldflags += " -Wl,-Bstatic,-mllvm,-gvn-max-recurse-depth=250"

        # Stage 1 build (libcxx, libcxxabi, libunwind)
        libcxx_inc = os.path.join(self.package_folder, "include", "c++", "v1")
        clang_inc = os.path.join(self.package_folder, "lib", "clang", self.version, "include")
        env = {
            "LD_LIBRARY_PATH": os.path.join(self.package_folder, "lib"),
            "LDFLAGS": ldflags,
            "CXXFLAGS": f" -nostdinc -nostdinc++ -isystem {clang_inc} -isystem {libc_inc}",
        }
        with tools.environment_append(env):
            cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage1-{self.version}")
            cmake.build(target="install-libcxx")
            cmake.build(target="install-unwind")
            cmake.build(target="install-compiler-rt")

        # Stage 2 build (lld, clang, libcxx, libcxxabi, libunwind)
        with tools.environment_append(env):
            cmake.configure(source_folder=f"llvm-{self.version}", build_folder=f"stage2-{self.version}")
            cmake.build(target="install-clang")
            cmake.build(target="install-clang-resource-headers")
            cmake.build(target="install-ar")
            cmake.build(target="install-ranlib")
            cmake.build(target="install-lld")
            cmake.build(target="install-libcxx")
            cmake.build(target="install-unwind")
            cmake.build(target="install-compiler-rt")
            cmake.build(target="install-llvm-config")
            cmake.build(target="install-llvm-tblgen")
        # Make lld default linker
        with tools.chdir(os.path.join(self.package_folder, "bin")):
            os.symlink("ld.lld", "ld")

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "clang")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "clang++")
        self.env_info.AR = os.path.join(self.package_folder, "bin", "ar")
        self.env_info.RANLIB = os.path.join(self.package_folder, "bin", "ranlib")
        self.env_info.LD = os.path.join(self.package_folder, "bin", "lld")

        if self.settings.libc_build == "musl":
            static_flags = "-static"
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-musl"].rootpath, "include")
        else:
            static_flags = "-static-libgcc -Wl,-Bstatic"
            libc_inc = os.path.join(self.deps_cpp_info["bootstrap-glibc"].rootpath, "include")
        clang_inc = os.path.join(self.package_folder, "lib", "clang", self.version, "include")
        libcxx_inc = os.path.join(self.package_folder, "include", "c++", "v1")

        self.env_info.CFLAGS = f"{static_flags} -flto=thin -nostdinc -isystem {clang_inc} -isystem {libc_inc}"
        self.env_info.CXXFLAGS = f"{static_flags} -flto=thin -nostdinc -nostdinc++ -isystem {libcxx_inc} -isystem {clang_inc} -isystem {libc_inc}"
