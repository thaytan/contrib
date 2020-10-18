import os

from conans import *


class LibjpegTurboConan(ConanFile):
    description = "JPEG image codec with accelerated baseline compression and decompression"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "yasm/1.3.0",
        "cmake/3.15.3",
    )
    requires = (
        "base/[^1.0.0]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/project/libjpeg-turbo/{self.version}/libjpeg-turbo-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["WITH_JPEG8"] = True
        cmake.definitions["CMAKE_INSTALL_LIBDIR"] = os.path.join(self.package_folder, "lib")
        cmake.definitions["CMAKE_INSTALL_INCLUDEDIR"] = os.path.join(self.package_folder, "include")
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()
