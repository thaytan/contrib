import os

from conans import *


class CppzmqConan(ConanFile):
    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("cmake/[^3.15.3]",)
    requires = (
        "base/[^1.0.0]",
        "libzmq/[^4.3.1]",
    )

    def source(self):
        tools.get(f"https://github.com/zeromq/cppzmq/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.install()

    def package(self):
        os.makedirs(os.path.join(self.package_folder, "lib", "pkgconfig"))
        with open(os.path.join(self.package_folder, "lib", "pkgconfig", "cppzmq.pc"), "w+") as pc_file:
            pc_file.write(f"prefix={self.package_folder}\n")
            pc_file.write("includedir=${prefix}/include\n")
            pc_file.write("Name: cppzmq\n")
            pc_file.write("Description: ZeroMQ core engine in C++\n")
            pc_file.write("Version: 4.3.0\n")
            pc_file.write("Cflags: -I${includedir}\n")
            pc_file.write("Requires: libzmq\n")
