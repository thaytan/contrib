import os

from conans import CMake, ConanFile, tools


class X265Conan(ConanFile):
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {"bit_depth": [8, 10, 12], "HDR10": [True, False]}
    default_options = "bit_depth=8", "HDR10=False"

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("cmake/[^3.15.3]")
        self.build_requires("yasm/[^1.3.0]")

    def source(self):
        tools.get("https://github.com/videolan/x265/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["HIGH_BIT_DEPTH"] = self.options.bit_depth != 8
        cmake.definitions["MAIN12"] = self.options.bit_depth == 12
        cmake.definitions["ENABLE_HDR10_PLUS"] = self.options.HDR10
        cmake.configure(source_folder=os.path.join("%s-%s" % (self.name, self.version), "source"))
        cmake.install()
