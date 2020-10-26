from conans import *


class ConanLibwebp(ConanFile):
    description = "library to encode and decode images in WebP format"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    build_requires = ("cmake/[^3.18.4]",)

    def source(self):
        tools.get(f"https://github.com/webmproject/libwebp/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIB"] = True
        cmake.configure(source_folder=f"libwebp-{self.version}")
        cmake.build()
        cmake.install()
