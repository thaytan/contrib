from build import *


class GTestRecipe(Recipe):
    description = "Google's C++ test framework"
    license = "BSD3"
    build_requires = ("cmake/[^3.15.3]",)

    def source(self):
        self.get(f"https://github.com/google/googletest/archive/release-{self.version}.tar.gz")

    def build(self):
        defs = {
            "BUILD_SHARED_LIBS": True,
        }
        self.cmake(defs)

