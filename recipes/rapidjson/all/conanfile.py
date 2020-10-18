from conans import *


class RapidJsonConan(ConanFile):
    description = "A fast JSON parser/generator for C++ with both SAX/DOM style API"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
    )

    def source(self):
        tools.get(f"https://github.com/Tencent/rapidjson/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["RAPIDJSON_HAS_STDSTRING"] = True
        cmake.definitions["RAPIDJSON_BUILD_CXX11"] = True
        cmake.definitions["RAPIDJSON_ENABLE_INSTRUMENTATION_OPT"] = True
        cmake.configure(source_folder=f"rapidjson-{self.version}")
        cmake.build()
        cmake.install()
