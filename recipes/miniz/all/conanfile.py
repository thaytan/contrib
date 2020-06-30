from conans import *


class MinuzConan(ConanFile):
    description = "Single C source file zlib-replacement library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "cmake/[^3.15.3]",
    )

    def source(self):
        tools.get(f"https://github.com/richgel999/miniz/archive/{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_dir=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()
