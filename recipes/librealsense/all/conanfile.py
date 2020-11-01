from build import *


class LibRealsenseRecipe(PythonRecipe):
    description = "Intel RealSense SDK"
    license = "Apache"
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
        # "cuda/[^10.1.243]",
    )
    requres = (
        "python/[^3.8.4]",
        "libusb/[^1.0.23]",
    )

    def source(self):
        self.get(f"https://github.com/IntelRealSense/librealsense/archive/v{self.version}.tar.gz")
        self.patch("pkgconfig-fix.patch")
        self.patch("libusb-fix.patch")

    def build(self):
        defs = {
            "PYTHON_LIBRARIES": os.path.join(self.deps_cpp_info["python"].rootpath, "lib", "libpython.so"),
            "PYTHON_INCLUDE_DIRS": os.path.join(self.deps_cpp_info["python"].rootpath, "include", f"python{self.settings.python}"),
            # "BUILD_WITH_CUDA": self.options.cuda,
            "BUILD_PYTHON_BINDINGS": True,
            "BUILD_EXAMPLES": False,
            "BUILD_GRAPHICAL_EXAMPLES": False,
            "BUILD_PCL_EXAMPLES": False,
            "BUILD_NODEJS_BINDINGS": False,
            "BUILD_UNIT_TESTS": False,
            "PYTHONLIBS_FOUND": True,
        }
        self.cmake(defs)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib"))
