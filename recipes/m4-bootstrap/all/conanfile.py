import os

from conans import *


class M4BootstrapConan(ConanFile):
    name = "m4-bootstrap"
    description = "The GNU macro processor"
    license = "GPL3"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/m4/m4-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"m4-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.make(target="install-strip")

    def package_info(self):
        self.env_info.M4 = os.path.join(self.package_folder, "bin", "m4")
