from conans import *


class IntelGmmlibConan(ConanFile):
    description = "Intel Graphics Memory Management Library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
    )

    def source(self):
        tools.get(f"https://github.com/intel/gmmlib/archive/intel-gmmlib-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=f"intel-gmmlib-{self.version}")
        cmake.build()
        cmake.install()
