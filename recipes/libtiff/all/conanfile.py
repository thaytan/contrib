from conans import *


class LibtiffConan(ConanFile):
    description = "Library for manipulation of TIFF images"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("mesa/20.0.0",)
    requires = (
        "base/[^1.0.0]",
        "zlib/[^1.2.11]",
        "libjpeg-turbo/[^2.0.4]",
    )

    def source(self):
        tools.get(f"https://download.osgeo.org/libtiff/tiff-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        with tools.chdir(f"tiff-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
