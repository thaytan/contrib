import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibRealsenseConan(ConanFile):
    version = "2.17.0"
    name = "librealsense"
    license = "https://raw.githubusercontent.com/IntelRealSense/librealsense/master/LICENSE"
    description = "Intel RealSense SDK https://realsense.intel.com"
    url = "https://github.com/ulricheck/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"
    requires = "libusb/1.0.22@bincrafters/stable"
    options = {"shared": [True, False]}
    default_options = "shared=True", "libusb:shared=True"
    generators = "pkg_config",
    exports = "libusb-fix.patch"

    def source(self):
        tools.get("https://github.com/IntelRealSense/librealsense/archive/v{0}.tar.gz".format(self.version))
        tools.patch(patch_file="libusb-fix.patch", base_path="librealsense-" + self.version)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_PCL_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_NODEJS_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_UNIT_TESTS"] = "OFF"
        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        else:
            cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"
        cmake.configure(source_dir="librealsense-" + self.version)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
