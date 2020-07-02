from conans import *


class ClangConan(ConanFile):
    description = "C language family frontend for LLVM"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("cmake/[^3.15.3]",)
    requires = (
        "generators/[^1.0.0]",
        "llvm/[^9.0.0]",
    )

    def source(self):
        tools.get(f"https://releases.llvm.org/{self.version}/cfe-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self, generator="Ninja", build_type="Release")
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.configure(source_folder=f"cfe-{self.version}.src")
        cmake.build()
        cmake.install()
