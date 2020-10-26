from conans import *


class CapNProtoConan(ConanFile):
    description = "Cap'n Proto serialization/RPC system"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cmake/[^3.18.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://github.com/capnproto/capnproto/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.configure(source_folder=f"capnproto-{self.version}")
        cmake.build()
        cmake.install()
