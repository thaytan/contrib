from conans import *


class CMakeConan(ConanFile):
    description = "A cross-platform open-source make system"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")

    def requirements(self):
        self.requires("cc/[^1.0.0]")
        self.requires("pkgconf/[^1.6.3]")
        self.requires("ninja/[^1.9.0]")

    def source(self):
        tools.get("https://github.com/Kitware/CMake/releases/download/v{0}/cmake-{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("./bootstrap --prefix=" + self.package_folder)
            self.run("make install")
