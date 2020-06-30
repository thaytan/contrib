from conans import *


class ConanLibwebp(ConanFile):
    description = "library to encode and decode images in WebP format"
    license = "BSD"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("cmake/[^3.15.3]")

    def source(self):
        tools.get("https://github.com/webmproject/libwebp/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
