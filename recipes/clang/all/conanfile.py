from conans import CMake, ConanFile, tools


class ClangConan(ConanFile):
    description = "C language family frontend for LLVM"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("llvm/[>=9.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://releases.llvm.org/{0}/cfe-{0}.src.tar.xz".format(self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja", build_type="Release")
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.configure(source_folder="cfe-%s.src" % self.version)
        cmake.build()
        cmake.install()
