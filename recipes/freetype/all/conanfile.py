from glob import glob
from os import path, remove

from conans import *


class FreetypeConan(ConanFile):
    description = "FreeType is a software library to render fonts"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)
    requires = (
        "base/[^1.0.0]",
        "harfbuzz/2.6.1",
    )

    def source(self):
        tools.get(f"https://git.savannah.gnu.org/cgit/freetype/freetype2.git/snapshot/freetype2-VER-{self.version}.tar.gz".replace(".", "-"))

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("freetype2-VER-" + self.version.replace(".", "-")):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
