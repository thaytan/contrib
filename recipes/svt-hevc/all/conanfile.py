import os

from conans import CMake, ConanFile, tools


class SvtHevcConan(ConanFile):
    license = "BSD"
    description = "The Scalable Video Technology for HEVC Encoder"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)
        self.build_requires("yasm/[>=1.3.0]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://github.com/OpenVisualCloud/SVT-HEVC/archive/v%s.tar.gz"
            % self.version
        )

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="SVT-HEVC-%s" % self.version)
        cmake.build()
        cmake.install()
