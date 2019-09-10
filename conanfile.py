import os
from conans import ConanFile, CMake, tools
from conans.util import files

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "3.4.6"
    except:
        return None

class OpenCVConan(ConanFile):
    name = "opencv"
    version = get_version()
    license = "https://raw.githubusercontent.com/IntelRealSense/librealsense/master/LICENSE"
    description = "OpenCV is an open source computer vision and machine learning software library."
    url = "https://gitlab.com/aivero/public/conan/conan-opencv"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("zlib/1.2.11@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/opencv/opencv/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_ZLIB'] = False
        cmake.definitions['BUILD_TIFF'] = False
        cmake.definitions['BUILD_JASPER'] = False
        cmake.definitions['BUILD_JPEG'] = False
        cmake.definitions['BUILD_PNG'] = False
        cmake.definitions['BUILD_OPENEXR'] = False
        cmake.definitions['BUILD_WEBP'] = False
        cmake.definitions['BUILD_TBB'] = False
        cmake.definitions['BUILD_IPP_IW'] = False
        cmake.definitions['BUILD_ITT'] = False
        cmake.definitions['BUILD_JPEG_TURBO_DISABLE'] = True

        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
