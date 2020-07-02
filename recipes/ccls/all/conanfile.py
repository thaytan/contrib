from conans import *


class CclsConan(ConanFile):
    description = "C/C++ language server supporting cross references, hierarchies, completion and semantic highlighting"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("cmake/[^3.15.3]",)
    requires = (
        "generators/[^1.0.0]",
        "clang/[^9.0.0]",
        "rapidjson/master",
    )

    def source(self):
        tools.get(f"https://github.com/MaskRay/ccls/archive/{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()
