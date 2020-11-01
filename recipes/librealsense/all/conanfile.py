from build import *


class LibRealsenseRecipe(Recipe):
    description = "Intel RealSense SDK"
    license = "Apache"
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
        # "cuda/[^10.1.243]",
    )
    requires = ("libusb/[^1.0.23]",)

    def source(self):
        self.get(f"https://github.com/IntelRealSense/librealsense/archive/v{self.version}.tar.gz")
        self.patch("pkgconfig-fix.patch")
        self.patch("libusb-fix.patch")

    def build(self):
        defs = {
            # "BUILD_WITH_CUDA": self.options.cuda,
            "BUILD_PYTHON_BINDINGS": False,
            "BUILD_EXAMPLES": False,
            "BUILD_GRAPHICAL_EXAMPLES": False,
            "BUILD_PCL_EXAMPLES": False,
            "BUILD_NODEJS_BINDINGS": False,
            "BUILD_UNIT_TESTS": False,
        }
        self.cmake(defs)
