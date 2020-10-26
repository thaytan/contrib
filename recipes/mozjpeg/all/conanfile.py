import os
from conans import *


class MozjpegConan(ConanFile):
    description = "JPEG image codec with accelerated baseline compression and decompression"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cmake/[^3.18.4]",
        "yasm/[^1.3.0]",
        "zlib/[^1.2.11]",
        "libpng/[^1.6.37]",
    )

    def source(self):
        tools.get(f"https://github.com/mozilla/mozjpeg/archive/v{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_SHARED"] = False
        cmake.definitions["CMAKE_INSTALL_BINDIR"] = os.path.join(self.package_folder, "bin")
        cmake.definitions["CMAKE_INSTALL_DATAROOTDIR"] = os.path.join(self.package_folder, "share")
        cmake.definitions["CMAKE_INSTALL_INCLUDEDIR"] = os.path.join(self.package_folder, "include")
        cmake.definitions["CMAKE_INSTALL_LIBDIR"] = os.path.join(self.package_folder, "lib")
        cmake.configure(source_folder=f"mozjpeg-{self.version}")
        cmake.build()
        cmake.install()
