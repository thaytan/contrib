from conans import *


class ConanLibwebp(ConanFile):
    description = "library to encode and decode images in WebP format"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("cmake/[^3.15.3]",)

    def source(self):
        tools.get(f"https://github.com/webmproject/libwebp/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()
