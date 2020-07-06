import os

from conans import *


class LibRealsenseConan(ConanFile):
    name = "librealsense"
    description = "Intel RealSense SDK"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    options = {"cuda": [True, False], "python": [True, False]}
    default_options = ("cuda=False", "python=True")

    def build_requirements(self):
        self.build_requires("cc/[^1.0.0]")
        self.build_requires("cmake/[^3.15.3]")
        if self.options.cuda:
            self.build_requires("cuda/[^10.1.243]")

    def requirements(self):
        self.requires("base/[^1.0.0]")
        self.requires("libusb/[^1.0.23]")
        if self.options.python:
            self.requires("python/[^3.7.4]")

    def source(self):
        tools.get(f"https://github.com/IntelRealSense/librealsense/archive/v{self.version}.tar.gz")
        tools.patch(patch_file="pkgconfig-fix.patch", base_path=f"{self.name}-{self.version}")
        tools.patch(patch_file="libusb-fix.patch", base_path=f"{self.name}-{self.version}")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_WITH_CUDA"] = self.options.cuda
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = self.options.python
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = False
        cmake.definitions["BUILD_PCL_EXAMPLES"] = False
        cmake.definitions["BUILD_NODEJS_BINDINGS"] = False
        cmake.definitions["BUILD_UNIT_TESTS"] = False
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib"))
