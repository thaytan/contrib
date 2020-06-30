from conans import *


class LibxtstConan(ConanFile):
    description = "X11 Testing Resource extension library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = (
        "libx11/[^1.6.8]",
        "libxext/[^1.3.4]",
        "libxfixes/[^5.0.3]",
        "libxi/[^1.7.1]",
    )

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXtst-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXtst-" + self.version):
            autotools.configure(args=args)
            autotools.install()
