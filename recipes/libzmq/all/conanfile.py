from conans import *


class LibzmqConan(ConanFile):
    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("cmake/[^3.15.3]",)

    def source(self):
        tools.get(f"https://github.com/zeromq/libzmq/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["ZMQ_BUILD_TESTS"] = False
        cmake.definitions["WITH_PERF_TOOL"] = False
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.install()
