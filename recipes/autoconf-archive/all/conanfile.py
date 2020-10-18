from conans import *


class AutoconfArchiveConan(ConanFile):
    description = "A collection of freely re-usable Autoconf macros"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autoconf/[^2.69]",)

    def source(self):
        tools.get(f"https://ftpmirror.gnu.org/autoconf-archive/autoconf-archive-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"autoconf-archive-{self.version}")
        autotools.install()
