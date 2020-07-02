from conans import *


class GTestConan(ConanFile):
    description = "Google's C++ test framework"
    license = "BSD-3-Clause"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("cmake/[^3.15.3]",)

    def source(self):
        tools.get(f"https://github.com/google/googletest/archive/release-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        cmake.configure(source_folder="googletest-release-" + self.version)
        cmake.install()
