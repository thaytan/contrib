from conans import *


class LibxrenderConan(ConanFile):
    description = "X Rendering Extension client library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "pkgconf/[^1.6.3]",
        "xorg-util-macros/[^1.19.1]",
        "xtrans/[^1.4.0]",
    )
    requires = ("libx11/[^1.6.8]",)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXrender-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXrender-%s" % self.version):
            autotools.configure(args=args)
            autotools.install()
