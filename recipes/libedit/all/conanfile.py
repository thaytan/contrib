import os

from conans import *


class LibeditConan(ConanFile):
    description = "System V Release 4.0 curses emulation library"
    license = "Zlib"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
        "pkgconf/[^1.6.3]",
    )
    requires = ("ncurses/[^6.1]",)

    def source(self):
        tools.get("https://thrysoee.dk/editline/libedit-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
