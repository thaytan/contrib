import os

from conans import *


class Sdl2Conan(ConanFile):
    description = "A library for portable low-level access to a video framebuffer, audio output, mouse, and keyboard"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
        requires = (
        "base/[^1.0.0]",
        "libxcb/[^1.13.1]",
        "libxext/[^1.3.4]",
    )

    def source(self):
        tools.get(f"https://www.libsdl.org/release/SDL2-{self.version}.tar.gz")

    def build(self):
        with tools.chdir("SDL2-" + self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
