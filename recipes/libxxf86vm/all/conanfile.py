from conans import *


class Libxxf86vmConan(ConanFile):
    description = "X11 XFree86 video mode extension library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("pkgconf/[^1.6.3]")
        self.build_requires("xorg-util-macros/[^1.19.1]")
        self.build_requires("xorgproto/[^2019.1]")

    def requirements(self):
        self.requires("libxext/[^1.3.4]")

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXxf86vm-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXxf86vm-" + self.version):
            autotools.configure()
            autotools.install()
