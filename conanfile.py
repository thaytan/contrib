import os

from conans import CMake, ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.28.1"
    except:
        return None

class LibRealsenseConan(ConanFile):
    name = "librealsense"
    version = get_version()
    license = "Apache"
    description = "Intel RealSense SDK"
    url = "https://gitlab.com/aivero/public/conan/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    options = {
        "cuda": [True, False],
    }
    default_options = (
        "cuda=False",
    )
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)
        if self.options.cuda:
            self.build_requires("cuda/[>=10.1.243]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("libusb/[>=1.0.23]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/IntelRealSense/librealsense/archive/v%s.tar.gz" % self.version)
        tools.patch(patch_file="pkgconfig-fix.patch", base_path="%s-%s" % (self.name, self.version))
        tools.patch(patch_file="libusb-fix.patch", base_path="%s-%s" % (self.name, self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = True
        cmake.definitions["BUILD_WITH_CUDA"] = self.options.cuda
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = False
        cmake.definitions["BUILD_PCL_EXAMPLES"] = False
        cmake.definitions["BUILD_NODEJS_BINDINGS"] = False
        cmake.definitions["BUILD_UNIT_TESTS"] = False
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib")
