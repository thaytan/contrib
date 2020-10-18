from conans import *


class MinuzConan(ConanFile):
    description = "Single C source file zlib-replacement library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("cmake/[^3.15.3]",)

    def source(self):
        tools.get(f"https://github.com/richgel999/miniz/archive/{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_dir=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()
