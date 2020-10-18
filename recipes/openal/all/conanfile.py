import os

from conans import *


class OpenalConan(ConanFile):
    description = "Cross-platform 3D audio library, software implementation"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("cmake/[^3.15.3]",)
    requires = (
        "base/[^1.0.0]",
        "libffi/3.3-rc0",
    )

    def source(self):
        tools.get(f"https://github.com/kcat/openal-soft/archive/openal-soft-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"openal-soft-openal-soft-{self.version}")
        cmake.build()
        cmake.install()
