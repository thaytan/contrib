import os

from conans import CMake, ConanFile, tools


class OpenCVConan(ConanFile):
    name = "opencv"
    version = tools.get_env("GIT_TAG", "3.4.6")
    description = "OpenCV is an open source computer vision and machine learning software library."
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD"
    settings = "os", "compiler", "build_type", "arch"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)
        self.requires("libpng/[>=1.6.37]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/opencv/opencv/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
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
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3.6", "dist-packages")
