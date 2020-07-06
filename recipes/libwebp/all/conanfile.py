from conans import *


class ConanLibwebp(ConanFile):
    name = "libwebp"
    description = "library to encode and decode images in WebP format"
    license = "BSD"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("cmake/[^3.15.3]",)

    def source(self):
        tools.get(f"https://github.com/webmproject/libwebp/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()
