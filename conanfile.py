import os

from conans import CMake, ConanFile, tools


class LLVMConan(ConanFile):
    name = "llvm"
    version = tools.get_env("GIT_TAG", "9.0.0")
    license = "custom", "Apache"
    description = (
        "Collection of modular and reusable compiler and toolchain technologies"
    )
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("libffi/3.3-rc0@%s/stable" % self.user)
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)
        self.requires("libxml2/[>=2.2.9]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://releases.llvm.org/{0}/llvm-{0}.src.tar.xz".format(self.version)
        )

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_FFI"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.configure(source_folder="%s-%s.src" % (self.name, self.version))
        cmake.build()
        cmake.install()
