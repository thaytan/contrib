import os

from conans import *


class RenderprotoConan(ConanFile):
    description = "X11 Render extension wire protocol"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

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
