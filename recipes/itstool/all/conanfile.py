import os

from conans import *


class ItstoolConan(ConanFile):
    description = "XML to PO and back again"
    license = "GPL3"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("autotools/[^1.0.0]",)
    requires = (
        "base/[^1.0.0]",
        "libxml2/[^2.9.9]",
        "python/[^3.7.4]",
    )

    def source(self):
        tools.get(f"https://github.com/itstool/itstool/archive/{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
