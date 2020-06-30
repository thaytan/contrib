from conans import *


class GiflibConan(ConanFile):
    description = "Library for reading and writing gif images"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/project/giflib/giflib-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.make()
            autotools.install(["PREFIX=" + self.package_folder])
