import os

from conans import *


class TclConan(ConanFile):
    description = "The Tcl scripting language"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/[^1.0.0]",
        "autotools/[^1.0.0]",
    )
    requires = ("zlib/[^1.2.11]",)

    def source(self):
        tools.get(f"https://downloads.sourceforge.net/sourceforge/tcl/tcl{self.version}-src.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(os.path.join(f"{self.name, self.version)}{"unix"}"):
            autotools.configure()
            autotools.install()
