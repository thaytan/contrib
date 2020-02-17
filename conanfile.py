import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class Sdl2Conan(ConanFile):
    name = "sdl2"
    version = tools.get_env("GIT_TAG", "2.0.10")
    description = "A library for portable low-level access to a video framebuffer, audio output, mouse, and keyboard"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxcb/[>=1.13.1]@%s/stable" % self.user)
        self.requires("libxext/[>=1.3.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://www.libsdl.org/release/SDL2-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("SDL2-" + self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
