from conans import *


class LibxdamageConan(ConanFile):
    description = "X11 damaged region extension library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("pkgconf/[^1.6.3]",)
    requires = (
        "base/[^1.0.0]",
        "libxfixes/[^5.0.3]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXdamage-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXdamage-" + self.version):
            autotools.configure()
            autotools.install()
