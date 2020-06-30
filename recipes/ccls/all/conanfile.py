from conans import *


class CclsConan(ConanFile):
    description = "C/C++ language server supporting cross references, hierarchies, completion and semantic highlighting"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "cmake/[^3.15.3]",
    )
    requires = (
        "clang/[^9.0.0]",
        "rapidjson/master",
    )

    def source(self):
        tools.get("https://github.com/MaskRay/ccls/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
