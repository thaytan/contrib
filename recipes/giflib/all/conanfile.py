from conans import *


class GiflibConan(ConanFile):
    description = "Library for reading and writing gif images"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/project/giflib/giflib-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.make()
            autotools.install(["PREFIX=" + self.package_folder])
