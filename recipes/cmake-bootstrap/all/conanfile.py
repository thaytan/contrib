from conans import *


class CmakeBootstrapConan(ConanFile):
    description = "A cross-platform open-source make system"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    requires = "openssl-bootstrap/[^3.0.0-alpha4]"

    def source(self):
        tools.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"cmake-{self.version}"):
            self.run(f"./bootstrap --verbose --prefix=${self.package_folder}")
            self.run(f'make DESTDIR="{self.package_folder}" install')
