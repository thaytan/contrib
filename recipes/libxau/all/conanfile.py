from conans import *


class LibxauConan(ConanFile):
    description = "X11 authorisation library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
        "pkgconf/[^1.6.3]",
    )
    requires = ("xorgproto/[^2019.1]",)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXau-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXau-" + self.version):
            autotools.configure(args=args)
            autotools.install()
