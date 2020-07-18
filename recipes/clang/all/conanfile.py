from conans import *


class ClangConan(ConanFile):
    name = "clang"
    description = "C language family frontend for LLVM"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = ("cmake-bootstrap/[^3.17.3]",)
    requires = (
        ("generators/[^1.0.0]", "private"),
        "llvm/[^10.0.0]",
        "compiler-rt/[^10.0.0]",
        # Prioritize llvm-bootstrap below llvm and compiler-rt
        ("llvm-bootstrap/[^10.0.0]", "private"),
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True

        # clang options
        cmake.definitions["CLANG_VENDOR"] = "Aivero"
        cmake.definitions["CLANG_BUILD_EXAMPLES"] = False
        cmake.definitions["CLANG_PLUGIN_SUPPORT"] = True
        cmake.definitions["CLANG_DEFAULT_CXX_STDLIB"] = "libc++"
        cmake.definitions["CLANG_DEFAULT_LINKER"] = "lld"
        cmake.definitions["CLANG_DEFAULT_UNWINDLIB"] = "libunwind"
        cmake.definitions["CLANG_DEFAULT_RTLIB"] = "compiler-rt"

        cmake.configure(source_folder=f"{self.name}-{self.version}.src")
        cmake.build()
        cmake.install()
