import os
from conans import *


class LibjpegTurboConan(ConanFile):
    description = "JPEG image codec with accelerated baseline compression and decompression"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
        "yasm/[^1.3.0]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/project/libjpeg-turbo/{self.version}/libjpeg-turbo-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["WITH_JPEG8"] = True
        cmake.definitions["CMAKE_INSTALL_LIBDIR"] = os.path.join(self.package_folder, "lib")
        cmake.definitions["CMAKE_INSTALL_INCLUDEDIR"] = os.path.join(self.package_folder, "include")
        cmake.definitions["ENABLE_STATIC"] = False
        cmake.configure(source_folder=f"libjpeg-turbo-{self.version}")
        cmake.build()
        cmake.install()
