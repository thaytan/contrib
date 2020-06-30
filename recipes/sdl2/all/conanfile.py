import os

from conans import *


class Sdl2Conan(ConanFile):
    description = "A library for portable low-level access to a video framebuffer, audio output, mouse, and keyboard"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("generators/1.0.0",)
    requires = (
        "libxcb/[^1.13.1]",
        "libxext/[^1.3.4]",
    )

    def source(self):
        tools.get("https://www.libsdl.org/release/SDL2-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("SDL2-" + self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
