import os

from conans import CMake, ConanFile, tools


class LLVMConan(ConanFile):
    name = "llvm"
    license = "custom", "Apache"
    description = "Collection of modular and reusable compiler and toolchain technologies"
    settings = "os", "compiler", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libffi/[>=3.3]@%s/stable" % self.user)
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/llvm/llvm-project/releases/download/llvmorg-{0}/llvm-{0}.src.tar.xz".format(self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja", build_type="Release")
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_FFI"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.configure(source_folder="%s-%s.src" % (self.name, self.version))
        cmake.build()
        cmake.install()
