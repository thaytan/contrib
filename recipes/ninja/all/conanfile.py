import os

from conans import *


class NinjaConan(ConanFile):
    description = "Small build system with a focus on speed"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/[^7.4.0]")
        self.build_requires("python/[^3.7.4]")

    def source(self):
        tools.get("https://github.com/ninja-build/ninja/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("python configure.py --bootstrap")

    def package(self):
        self.copy(os.path.join("%s-%s" % (self.name, self.version), "ninja"), "bin", keep_path=False)
