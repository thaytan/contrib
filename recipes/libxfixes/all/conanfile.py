from conans import *


class LibxfixesConan(ConanFile):
    description = "X11 miscellaneous 'fixes' extension library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "pkgconf/[^1.6.3]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = ("libx11/[^1.6.8]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXfixes-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXfixes-" + self.version):
            autotools.configure(args=args)
            autotools.install()
