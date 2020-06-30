import os

from conans import *


class TclConan(ConanFile):
    description = "The Tcl scripting language"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/[^1.0.0]")
        self.build_requires("autotools/[^1.0.0]")

    def requirements(self):
        self.requires("zlib/[^1.2.11]")

    def source(self):
        tools.get("https://downloads.sourceforge.net/sourceforge/tcl/tcl%s-src.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(os.path.join("%s%s" % (self.name, self.version), "unix")):
            autotools.configure()
            autotools.install()
