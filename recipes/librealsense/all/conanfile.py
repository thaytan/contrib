from build import *


class LibRealsenseRecipe(Recipe):
    description = "Intel RealSense SDK"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    build_requires = (
        "cmake/[^3.18.4]",
        # "cuda/[^10.1.243]",
        "libusb/[^1.0.23]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/IntelRealSense/librealsense/archive/v{self.version}.tar.gz")
        self.patch("pkgconfig-fix.patch")
        self.patch("libusb-fix.patch")

    def build(self):
        defs = {
            # "BUILD_WITH_CUDA": self.options.cuda,
            "BUILD_PYTHON_BINDINGS": True,
            "BUILD_EXAMPLES": False,
            "BUILD_GRAPHICAL_EXAMPLES": False,
            "BUILD_PCL_EXAMPLES": False,
            "BUILD_NODEJS_BINDINGS": False,
            "BUILD_UNIT_TESTS": False,
            "PYTHON_INCLUDE_DIRS": os.path.join(self.deps_cpp_info["python"].rootpath, "include", "python3.8"),
            "PYTHON_LIBRARIES": os.path.join(self.deps_cpp_info["python"].rootpath, "lib", "libpython.a"),
            "PYTHONLIBS_FOUND": True,
            "PYTHON_MODULE_EXTENSION": "a",
        }
        self.cmake(defs)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib"))
