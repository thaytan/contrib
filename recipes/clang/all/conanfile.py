import shutil
import os
from conans import *


class ClangConan(ConanFile):
    description = "C language family frontend for LLVM"
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
    requires = (
        "libc/[^1.0.0]",
        "libcxx/[^10.0.1]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/lld-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/compiler-rt-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        shutil.move(f"clang-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "clang"))
        shutil.move(f"lld-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "lld"))
        shutil.move(f"compiler-rt-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "compiler-rt"))

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
        cmake.definitions["CLANG_DEFAULT_UNWINDLIB"] = "libgcc"
        cmake.definitions["CLANG_DEFAULT_RTLIB"] = "compiler-rt"
        cmake.definitions["CLANG_ENABLE_STATIC_ANALYZER"] = True
        cmake.definitions["LIBCLANG_BUILD_STATIC"] = True

        # compiler-rt options
        cmake.definitions["COMPILER_RT_BUILD_SANITIZERS"] = False
        cmake.definitions["COMPILER_RT_BUILD_XRAY"] = False
        cmake.definitions["COMPILER_RT_BUILD_LIBFUZZER"] = False

        cmake.configure(source_folder=f"llvm-{self.version}")
        cmake.build(target="install-compiler-rt")
        cmake.build(target="install-clang")
        cmake.build(target="install-clang-resource-headers")
        cmake.build(target="install-ar")
        cmake.build(target="install-objcopy")
        cmake.build(target="install-objdump")
        cmake.build(target="install-nm")
        cmake.build(target="install-lld")
        cmake.build(target="install-ranlib")
        cmake.build(target="install-strip")
        cmake.build(target="install-llvm-as")
        cmake.build(target="install-llvm-config")
        cmake.build(target="install-llvm-tblgen")
        cmake.build(target="install-llvm-profdata")

        # Create symlinks
        os.makedirs("bin_symlinks")
        with tools.chdir("bin_symlinks"):
            for dst in ["cc", "c++"]:
                os.symlink("clang-10", dst)
            for dst in ["clang", "clang++", "clang-cl", "clang-cpp"]:
                os.remove(os.path.join(self.package_folder, "bin", dst))
                os.symlink("clang-10", dst)
            for dst in ["ar", "nm", "objdump"]:
                os.remove(os.path.join(self.package_folder, "bin", dst))
                os.symlink(f"llvm-{dst}", dst)
            for dst in ["ld.lld", "ld64.lld", "lld-link", "wasm-ld"]:
                os.remove(os.path.join(self.package_folder, "bin", dst))
                os.symlink("lld", dst)
            os.symlink("lld", "ld")
            os.remove(os.path.join(self.package_folder, "bin", "strip"))
            os.symlink("llvm-objcopy", "strip")
            os.remove(os.path.join(self.package_folder, "bin", "ranlib"))
            os.symlink("llvm-ar", "ranlib")

        # Use system libgcc_s
        os.makedirs("lib_symlinks")
        with tools.chdir("lib_symlinks"):
            os.symlink(f"/lib/{arch}-linux-gnu/libgcc_s.so.1", "libgcc_s.so")

    def package(self):
        self.copy("*bin_symlinks/*", dst="bin", keep_path=False, symlinks=True)
        self.copy("*lib_symlinks/*", dst="lib", keep_path=False, symlinks=True)

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
            libc_inc = os.path.join(self.deps_cpp_info["musl"].rootpath, "include")
        else:
            static_flags = ""
            libc_inc = os.path.join(self.deps_cpp_info["glibc-headers"].rootpath, "include")
        clang_inc = os.path.join(self.package_folder, "lib", "clang", self.version, "include")
        libcxx_inc = os.path.join(self.deps_cpp_info["libcxx"].rootpath, "include", "c++", "v1")
        # -Wno-unused-command-line-argument is needed for some sanity tests in cmake
        cflags = f" -nostdinc -idirafter {clang_inc} -idirafter {libc_inc} {static_flags} -fPIC -flto=thin -Wno-unused-command-line-argument "
        cxxflags = f" -nostdinc++ -idirafter {libcxx_inc} {cflags} "

        self.env_info.CFLAGS = cflags
        self.env_info.CXXFLAGS = cxxflags
