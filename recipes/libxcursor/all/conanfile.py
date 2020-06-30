from conans import *


class LibxcursorConan(ConanFile):
    description = "X cursor management library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autotools/[^1.0.0]")
        self.build_requires("xorg-util-macros/[^1.19.1]")

    def requirements(self):
        self.requires("libxrender/[^0.9.10]")
        self.requires("libxfixes/[^5.0.3]")

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXcursor-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXcursor-%s" % self.version):
            autotools.configure(args=args)
            autotools.install()
