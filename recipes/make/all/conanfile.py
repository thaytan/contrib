import os
from conans import *


class MakeConan(ConanFile):
    description = "GNU make utility to maintain groups of programs"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = "cc/[^1.0.0]"

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/make/make-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"make-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.MAKE = os.path.join(self.package_folder, "bin", "make")
