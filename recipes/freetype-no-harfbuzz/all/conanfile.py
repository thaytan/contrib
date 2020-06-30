from glob import glob
from os import path, remove

from conans import *


class FreetypeNoHarfbuzzConan(ConanFile):
    description = "FreeType is a software library to render fonts"
    license = "GPL2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get("https://git.savannah.gnu.org/cgit/freetype/freetype2.git/snapshot/freetype2-VER-%s.tar.gz" % self.version.replace(".", "-"))

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("freetype2-VER-" + self.version.replace(".", "-")):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
