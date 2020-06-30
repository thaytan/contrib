from glob import glob
from os import path, remove

from conans import *


class LibuuidConan(ConanFile):
    description = "Portable uuid C library"
    license = "BSD-3-Clause"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("generators/1.0.0",)

    def source(self):
        tools.get("https://netix.dl.sourceforge.net/project/libuuid/libuuid-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
