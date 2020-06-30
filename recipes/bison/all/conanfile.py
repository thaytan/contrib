import os

from conans import *


class BisonConan(ConanFile):
    description = "Bison is a general-purpose parser generator"
    license = "GPL-3.0-or-later"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("generators/1.0.0",)
    requires = ("m4/[^1.4.18]",)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/bison/bison-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.BISON_PKGDATADIR = os.path.join(self.package_folder, "share", "bison")
