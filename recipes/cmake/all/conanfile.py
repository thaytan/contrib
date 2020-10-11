from conans import *


class CMakeConan(ConanFile):
    description = "A cross-platform open-source make system"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-cmake/[^3.18.0]",
        "bootstrap-ninja/[^1.10.0]",
        "clang/[^10.0.1]",
        "pkgconf/[^1.7.3]",
        "openssl/[^3.0.0-alpha6]",
    )

    def source(self):
        tools.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=f"cmake-{self.version}")
        cmake.build()
        cmake.install()

