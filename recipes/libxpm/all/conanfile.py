from conans import *


class LibxpmConan(ConanFile):
    name = "libxpm"
    description = "X11 pixmap library"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = (
        "base/[^1.0.0]",
        "libx11/[^1.6.8]",
        "libxext/[^1.3.4]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXpm-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXpm-" + self.version):
            autotools.configure(args=args)
            autotools.install()
