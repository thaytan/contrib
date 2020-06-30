from conans import *


class LibtiffConan(ConanFile):
    description = "Library for manipulation of TIFF images"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "mesa/20.0.0",
    )
    requires = (
        "zlib/[^1.2.11]",
        "libjpeg-turbo/[^2.0.4]",
    )

    def source(self):
        tools.get("https://download.osgeo.org/libtiff/tiff-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("tiff-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
