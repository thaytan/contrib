import os

from conans import *


class NinjaConan(ConanFile):
    description = "Small build system with a focus on speed"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cc/[^1.0.0]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/ninja-build/ninja/archive/v{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("python configure.py --bootstrap")

    def package(self):
        self.copy(os.path.join(f"{self.name}-{self.version}", "ninja"), "bin", keep_path=False)
