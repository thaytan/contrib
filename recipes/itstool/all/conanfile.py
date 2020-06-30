import os

from conans import *


class ItstoolConan(ConanFile):
    description = "XML to PO and back again"
    license = "GPL3"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
    )
    requires = (
        "libxml2/[^2.9.9]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get("https://github.com/itstool/itstool/archive/%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
