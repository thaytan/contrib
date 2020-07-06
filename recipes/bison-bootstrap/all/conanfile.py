import os

from conans import *


class BisonBoostrapConan(ConanFile):
    name = "bison-bootstrap"
    description = "Bison is a general-purpose parser generator"
    license = "GPL-3.0-or-later"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/bison/bison-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"bison-{self.version}"):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.BISON_PKGDATADIR = os.path.join(self.package_folder, "share", "bison")
