from conans import *


class LibxiConan(ConanFile):
    description = "X11 Input extension library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autotools/[^1.0.0]")
        self.build_requires("xorg-util-macros/[^1.19.1]")

    def requirements(self):
        self.requires("libx11/[^1.6.8]")
        self.requires("libxext/[^1.3.4]")
        self.requires("libxfixes/[^5.0.3]")

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXi-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXi-" + self.version):
            autotools.configure(args=args)
            autotools.install()
