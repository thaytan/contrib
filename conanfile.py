import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibRealsenseConan(ConanFile):
    version = "2.17.0"
    name = "librealsense"
    license = "https://raw.githubusercontent.com/IntelRealSense/librealsense/master/LICENSE"
    description = "Intel RealSense SDK https://realsense.intel.com"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/ulricheck/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports = "libusb-fix.patch"

    def requirements(self):
        self.requires("libusb/1.0.22@%s/%s" % (self.user, self.channel))
    
    def source(self):
        tools.get("https://github.com/IntelRealSense/librealsense/archive/v{0}.tar.gz".format(self.version))
        tools.patch(patch_file="libusb-fix.patch", base_path="librealsense-" + self.version)

    def build(self):
        vars = {'PKG_CONFIG_LIBUSB_1_0_PREFIX': self.deps_cpp_info["libusb"].rootpath}
        with tools.environment_append(vars):
            os.system("pkg-config --cflags libusb-1.0")
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
