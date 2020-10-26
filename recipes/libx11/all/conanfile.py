import os
from conans import *


class Libx11Conan(ConanFile):
    description = "X11 client-side library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "xorg-util-macros/[^1.19.2]",
        "xtrans/[^1.4.0]",
        "xorgproto/[^2020.1]",
        "perl/[^5.30.0]",
    )
    requires = ("libxcb/[^1.14]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libX11-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libX11-{self.version}", args)
        autotools.install()

    def package_info(self):
        self.env_info.XLOCALEDIR = os.path.join(self.package_folder, "share", "X11", "locale")
