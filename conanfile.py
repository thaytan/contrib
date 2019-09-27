from conans import ConanFile, CMake, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.28.0"
    except:
        return None

class LibRealsenseConan(ConanFile):
    name = "librealsense"
    version = get_version()
    license = "Apache"
    description = "Intel RealSense SDK https://realsense.intel.com"
    url = "https://gitlab.com/aivero/public/conan/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("libusb/[>=1.0.23]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/IntelRealSense/librealsense/archive/v%s.tar.gz" % self.version)
        tools.patch(patch_file="pkgconfig-fix.patch", base_path="librealsense-" + self.version)
        tools.patch(patch_file="libusb-fix.patch", base_path="librealsense-" + self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_PCL_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_NODEJS_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = "ON"
        cmake.definitions["BUILD_UNIT_TESTS"] = "OFF"
        cmake.configure(source_folder="librealsense-" + self.version)
        cmake.build()
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")
            self.copy("*.h", "src")
            self.copy("*.c", "src")

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib")
