import os

from conans import *


class RenderprotoConan(ConanFile):
    name = "renderproto"
    description = "X11 Render extension wire protocol"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/proto/renderproto-{self.version}.tar.gz")
        with tools.chdir(f"{self.name}-{self.version}"):
            os.remove("config.guess")
            os.remove("config.sub")
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD", "config.guess")
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD", "config.sub")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()
