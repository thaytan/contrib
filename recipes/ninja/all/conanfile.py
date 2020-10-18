from conans import *


class NinjaConan(ConanFile):
    description = "Small build system with a focus on speed"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-cmake/[^3.18.0]",
        "bootstrap-ninja/[^1.10.0]",
        "cc/[^1.0.0]",
    )

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
