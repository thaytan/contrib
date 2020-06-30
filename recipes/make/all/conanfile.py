import os

from conans import *


class MakeConan(ConanFile):
    description = "GNU make utility to maintain groups of programs"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "bootstrap-gcc/7.4.0",
        "bootstrap-make/4.3",
    )

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/make/make-{}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.MAKE = os.path.join(self.package_folder, "bin", "make")
