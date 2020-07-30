import os

from conans import *


class MakeBootstrapConan(ConanFile):
    name = "make-bootstrap"
    description = "GNU make utility to maintain groups of programs"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = "llvm-bootstrap/[^10.0.0]"

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/make/make-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"{self.name}-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.MAKE = os.path.join(self.package_folder, "bin", "make")
