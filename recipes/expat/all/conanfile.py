from conans import *


class ExpatConan(ConanFile):
    description = "An XML parser library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
    )

    def source(self):
        tools.get("https://github.com/libexpat/libexpat/releases/download/R_{0}/expat-{1}.tar.bz2".format(self.version.replace(".", "_"), self.version))

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure(args=args)
            autotools.install()
