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
        tools.get("https://downloads.sourceforge.net/project/giflib/giflib-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.make()
            autotools.install(["PREFIX=" + self.package_folder])
