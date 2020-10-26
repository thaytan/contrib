from conans import *


class OpenCVConan(ConanFile):
    description = "OpenCV is an open source computer vision and machine learning software library."
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cmake/[^3.18.3]",
        "zlib/[^1.2.11]",
        "libpng/[^1.6.37]",
    )

    def source(self):
        tools.get(f"https://github.com/opencv/opencv/archive/{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["OPENCV_GENERATE_PKGCONFIG"] = True
        cmake.definitions["BUILD_ZLIB"] = True
        cmake.definitions["BUILD_PNG"] = True
        cmake.definitions["BUILD_TIFF"] = False
        cmake.definitions["BUILD_JASPER"] = False
        cmake.definitions["BUILD_JPEG"] = False
        cmake.definitions["BUILD_OPENEXR"] = False
        cmake.definitions["BUILD_WEBP"] = False
        cmake.definitions["BUILD_TBB"] = False
        cmake.definitions["BUILD_IPP_IW"] = False
        cmake.definitions["BUILD_ITT"] = False
        cmake.definitions["BUILD_JPEG_TURBO_DISABLE"] = True
        cmake.configure(source_folder=f"opencv-{self.version}")
        cmake.build()
        cmake.install()
