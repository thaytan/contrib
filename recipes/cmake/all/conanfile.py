from conans import *


class CMakeConan(ConanFile):
    description = "A cross-platform open-source make system"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    requires = (
        "base/[^1.0.0]",
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "ninja/[^1.9.0]",
    )

    def source(self):
        tools.get(f"https://github.com/Kitware/CMake/releases/download/v{self.version}/cmake-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("./bootstrap --prefix=" + self.package_folder)
            self.run("make install")
