import os
from conans import CMake, ConanFile, tools


class KinectAzureSensorSDKConan(ConanFile):
    name = "k4a"
    version = tools.get_env("GIT_TAG", "1.3.0")
    license = "MIT"
    description = "Azure Kinect SDK"
    url = "https://gitlab.com/aivero/public/conan/conan-k4a"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"
    exports = "patches/disable_build_of_examples_and_tools.patch"
    repo = "Azure-Kinect-Sensor-SDK"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("glfw/[>=3.3]@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)

    def source(self):
        # Clone `Azure-Kinect-Sensor-SDK` repo
        git = tools.Git(folder=self.repo)
        git.clone(
            "https://github.com/microsoft/%s.git" % self.repo, branch="release/%s.x" % self.version[:3])

        # Disable building of examples and tools
        tools.patch(base_path=self.repo,
                    patch_file="patches/disable_build_of_examples_and_tools.patch")

    def build(self):
        # Build
        cmake = CMake(self, generator="Ninja")
        cmake.configure(
            source_folder=self.repo)
        cmake.build()
        cmake.install()

        # Download `libk4a` and extract `libdepthengine`
        libk4a_deb = "libk4a%s_%s_%s.deb" % (
            self.version[:3], self.version, "amd64")
        tools.download(
            "https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a%s/%s" % (self.version[:3], libk4a_deb), filename=libk4a_deb
        )
        self.run("dpkg -x %s libk4a" % libk4a_deb)
        self.run("find -iname 'libdepthengine.*' -exec cp {} %s \;" %
                 os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib")
