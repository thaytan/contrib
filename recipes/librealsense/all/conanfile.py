import os

from conans import CMake, ConanFile, tools


class LibRealsenseConan(ConanFile):
    description = "Intel RealSense SDK"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports = "libusb-fix.patch", "pkgconfig-fix.patch"
    options = {"cuda": [True, False], "python": [True, False]}
    default_options = ("cuda=False", "python=True")

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)
        if self.options.cuda:
            self.build_requires("cuda/[>=10.1.243]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libusb/[>=1.0.23]@%s/stable" % self.user)
        if self.options.python:
            self.requires("python/[>=3.7.4]@%s/stable" % self.user)

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
