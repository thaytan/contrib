from conans import *


class ClangConan(ConanFile):
    name = "clang"
    description = "C language family frontend for LLVM"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    requires = (
        "base/[^1.0.0]",
        "llvm/[^10.0.0]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.configure(source_folder=f"{self.name}-{self.version}.src")
        cmake.build()
        cmake.install()
