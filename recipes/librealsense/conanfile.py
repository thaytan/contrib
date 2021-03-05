from build import *


class LibRealsenseRecipe(PythonRecipe):
    description = "Intel RealSense SDK"
    license = "Apache"
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    options = {"cuda": [True, False], "python": [True, False]}
    default_options = ("cuda=True", "python=True")
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
    )
    requires = ("libusb/[^1.0.23]",)

    def requirements(self):
        if self.options.cuda:
            self.requires("cuda/[^11.2.1]")
        if self.options.python:
            self.requires(f"python/[^3.8]")

    def source(self):
        self.get(f"https://github.com/IntelRealSense/librealsense/archive/v{self.version}.tar.gz")
        self.patch("pkgconfig-fix.patch")
        self.patch("libusb-fix.patch")

    def build(self):
        defs = {
            "BUILD_WITH_CUDA": self.options.cuda,
            "BUILD_WITH_PYTHON": self.options.python,
            "BUILD_PYTHON_BINDINGS": False,
            "BUILD_EXAMPLES": False,
            "BUILD_GRAPHICAL_EXAMPLES": False,
            "BUILD_PCL_EXAMPLES": False,
            "BUILD_NODEJS_BINDINGS": False,
            "BUILD_UNIT_TESTS": False,
        }
        self.cmake(defs)
