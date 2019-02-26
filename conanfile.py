import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibRealsenseConan(ConanFile):
    name = "librealsense"
    version = "2.17.0"
    license = "https://raw.githubusercontent.com/IntelRealSense/librealsense/master/LICENSE"
    description = "Intel RealSense SDK https://realsense.intel.com"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/ulricheck/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    folder_name = name + "-" + version
    no_copy_source = True

    def requirements(self):
        self.requires("libusb/1.0.22@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/IntelRealSense/librealsense/archive/v%s.tar.gz" % self.version)
        tools.patch(patch_file="libusb-fix.patch", base_path="librealsense-" + self.version)
        tools.patch(patch_file="pkgconfig-fix.patch", base_path="librealsense-" + self.version)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_PCL_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_NODEJS_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_UNIT_TESTS"] = "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = ("ON" if self.options.shared else "OFF")
        vars = {
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
            "CXXFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
        }
        with tools.environment_append(vars):
            cmake.configure(source_folder=self.folder_name, build_folder="build")
            cmake.build()
            cmake.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
