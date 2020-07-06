from conans import *


class LlvmConan(ConanFile):
    description = "Collection of modular and reusable compiler and toolchain technologies"
    license = "custom", "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    requires = ("base/[^1.0.0]", "libcxx/[^1.0.0]")

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")

    def build(self):
        env = {
            "CC": "gcc",
        }
        with tools.environment_append(env):
            cmake = CMake(self, generator="Ninja")
            cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
            cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
            cmake.definitions["LLVM_INSTALL_UTILS"] = True
            cmake.definitions["LLVM_ENABLE_FFI"] = True
            cmake.definitions["LLVM_ENABLE_RTTI"] = True
            cmake.definitions["CLANG_DEFAULT_CXX_STDLIB"] = "libc++"
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-U_FORTIFY_SOURCE"
            cmake.configure(source_folder=f"{self.name}-{self.version}.src")
            cmake.build()
            cmake.install()
