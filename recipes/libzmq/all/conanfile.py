from conans import *


class LibzmqConan(ConanFile):
    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "cmake/[^3.15.3]",
    )

    def source(self):
        tools.get("https://github.com/zeromq/libzmq/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["ZMQ_BUILD_TESTS"] = False
        cmake.definitions["WITH_PERF_TOOL"] = False
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.install()
