from glob import glob
from os import path, remove

from conans import *


class HarfbuzzConan(ConanFile):
    description = "HarfBuzz text shaping engine"
    license = "Old MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
        "freetype-no-harfbuzz/[^2.10.1]",
    )
    requires = ("glib/[^2.62.0]",)

    def source(self):
        tools.get(f"https://github.com/harfbuzz/harfbuzz/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
