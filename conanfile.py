import os
from conans import ConanFile, tools

class KinectAzureSensorSDKConan(ConanFile):
    name = "k4a"
    version = tools.get_env("GIT_TAG", "1.4.0")
    license = "MIT"
    description = "Azure Kinect SDK"
    url = "https://gitlab.com/aivero/public/conan/conan-k4a"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"
    exports = "k4a.pc"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)

    def source(self):
        version_short=self.version[:3]
        arch = self.settings.arch
        debian_repo_url = ""
        if arch == "x86_64":
            arch = "amd64"
            debian_repo_url="https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk"
        if arch == "armv8":
            arch = "arm64"
            debian_repo_url="https://packages.microsoft.com/ubuntu/18.04/multiarch/prod/pool/main/libk/"

        libk4a = "libk4a%s_%s_%s.deb" % (version_short, self.version, arch)
        libk4a_dev = "libk4a%s-dev_%s_%s.deb" % (version_short, self.version, arch)

        # Download `libk4a` and `libk4a-dev` for headers and shared objects
        tools.download("%s/libk4a%s/%s" % (debian_repo_url, version_short, libk4a), filename=libk4a)
        tools.download("%s/libk4a%s-dev/%s" % (debian_repo_url, version_short, libk4a_dev),  filename=libk4a_dev)

        # Extract shared objects, including the closed-source `libdepthengine.so*`
        self.run("dpkg -x %s libk4a" % libk4a)
        # Extract headers
        self.run("dpkg -x %s libk4a" % libk4a_dev)


    def package(self):
        tools.replace_prefix_in_pc_file("k4a.pc", self.package_folder)
        x = os.listdir("libk4a/usr/lib")
        print(x)
        self.copy("*", src="libk4a/usr/include", dst="include")
        self.copy("*", src="libk4a/usr/lib/" + x[0], dst="lib")
        self.copy("k4a.pc", dst="lib/pkgconfig")
        

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib")
