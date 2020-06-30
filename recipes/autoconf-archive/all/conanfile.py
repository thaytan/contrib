import os

from conans import *


class AutoconfArchiveConan(ConanFile):
    description = "A collection of freely re-usable Autoconf macros"
    license = "GPL3"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autoconf/[^2.69]")

    def source(self):
        tools.get("https://ftpmirror.gnu.org/autoconf-archive/autoconf-archive-%s.tar.xz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
