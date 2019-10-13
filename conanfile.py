from conans import CMake, ConanFile, tools


class ClangConan(ConanFile):
    name = "clang"
    version = tools.get_env("GIT_TAG", "9.0.0")
    license = "Apache"
    description = "C language family frontend for LLVM"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("llvm/[>=9.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://releases.llvm.org/{0}/cfe-{0}.src.tar.xz".format(self.version)
        )

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["LLVM_BUILD_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_LINK_LLVM_DYLIB"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.configure(source_folder="cfe-%s.src" % self.version)
        cmake.build()
        cmake.install()
