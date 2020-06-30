from conans import *


class LibxshmfenceConan(ConanFile):
    description = "Library that exposes a event API on top of Linux futexes"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "pkgconf/[^1.6.3]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = ("xorgproto/[^2019.1]",)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libxshmfence-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure(args=args)
            autotools.install()
