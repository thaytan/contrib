from conans import *


class LibxextConan(ConanFile):
    description = "X11 miscellaneous extensions library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "pkgconf/[^1.6.3]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = ("libx11/[^1.6.8]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXext-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXext-" + self.version):
            autotools.configure(args=args)
            autotools.install()
