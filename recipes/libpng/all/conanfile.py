from conans import *


class LibpngConan(ConanFile):
    description = "A collection of routines used to create PNG format graphics files"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("autotools/1.0.0",)
    requires = (
        "generators/1.0.0",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/sourceforge/libpng/libpng-{self.version}.tar.xz")

    def build(self):
        args = ["--disable-static"]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
