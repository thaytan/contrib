from conans import *


class XtransConan(ConanFile):
    description = "X transport library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/xtrans-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"xtrans-{self.version}")
        autotools.install()
