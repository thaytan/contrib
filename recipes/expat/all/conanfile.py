from conans import *


class ExpatConan(ConanFile):
    description = "An XML parser library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("cc/[^1.0.0]",)

    def source(self):
        tools.get(f"https://github.com/libexpat/libexpat/releases/download/R_{self.version.replace('.', '_')}/expat-{self.version}.tar.bz2")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure(args=args)
            autotools.install()
