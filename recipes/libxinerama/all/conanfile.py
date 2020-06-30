from conans import *


class LibxineramaConan(ConanFile):
    description = "X11 Xinerama extension library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = ("libxext/[^1.3.4]",)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXinerama-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXinerama-" + self.version):
            autotools.configure(args=args)
            autotools.install()
