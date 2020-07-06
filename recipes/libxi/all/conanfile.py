from conans import *


class LibxiConan(ConanFile):
    description = "X11 Input extension library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = (
        "base/[^1.0.0]",
        "libx11/[^1.6.8]",
        "libxext/[^1.3.4]",
        "libxfixes/[^5.0.3]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXi-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXi-" + self.version):
            autotools.configure(args=args)
            autotools.install()
