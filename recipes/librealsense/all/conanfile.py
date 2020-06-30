import os

from conans import *


class LibRealsenseConan(ConanFile):
    description = "Intel RealSense SDK"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    options = {"cuda": [True, False], "python": [True, False]}
    default_options = ("cuda=False", "python=True")
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
        "cmake/[^3.15.3]",
        if self.options.cuda:
            self.build_requires("cuda/[^10.1.243]")
    )
    requires = (
        "libusb/[^1.0.23]",
        if self.options.python:
            "python/[^3.7.4]",
    )

    def source(self):
        tools.get("https://github.com/IntelRealSense/librealsense/archive/v%s.tar.gz" % self.version)
        tools.patch(patch_file="pkgconfig-fix.patch", base_path="%s-%s" % (self.name, self.version))
        tools.patch(patch_file="libusb-fix.patch", base_path="%s-%s" % (self.name, self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_WITH_CUDA"] = self.options.cuda
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = self.options.python
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = False
        cmake.definitions["BUILD_PCL_EXAMPLES"] = False
        cmake.definitions["BUILD_NODEJS_BINDINGS"] = False
        cmake.definitions["BUILD_UNIT_TESTS"] = False
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib"))
