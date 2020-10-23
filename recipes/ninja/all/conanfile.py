from conans import *


class NinjaConan(ConanFile):
    description = "Small build system with a focus on speed"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"bootstrap": [True, False]}
    default_options = ("bootstrap=False",)

    def build_requirements(self):
        if self.options.bootstrap:
            self.build_requires("cmake/[^3.18.4]")
        else:
            self.build_requires("llvm/[^11.0.0]")

    def configure(self):
        # Avoid circular requirement
        self.options["cmake"].bootstrap = self.options.bootstrap

    def source(self):
        tools.get(f"https://github.com/ninja-build/ninja/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=f"ninja-{self.version}")
        cmake.build()

    def package(self):
        self.copy("ninja", "bin")

    def package_info(self):
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
