from conans import *


class XorgUtilMacrosConan(ConanFile):
    description = "X.Org Autotools macros"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/util/util-macros-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"util-macros-{self.version}")
        autotools.install()
