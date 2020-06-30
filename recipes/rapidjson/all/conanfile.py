import os

from conans import CMake, ConanFile, tools


class RapidJsonConan\(ConanFile\):
    description = "A fast JSON parser/generator for C++ with both SAX/DOM style API"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/Tencent/rapidjson/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["RAPIDJSON_HAS_STDSTRING"] = True
        cmake.definitions["RAPIDJSON_BUILD_CXX11"] = True
        cmake.definitions["RAPIDJSON_ENABLE_INSTRUMENTATION_OPT"] = True
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
