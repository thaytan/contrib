from conans import *


class LibxfixesConan(ConanFile):
    description = "X11 miscellaneous 'fixes' extension library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.2]",
    )
    requires = ("libx11/[^1.6.12]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXfixes-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libXfixes-{self.version}", args)
        autotools.install()
