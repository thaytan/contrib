from conans import *


class Help2ManConan(ConanFile):
    description = "Conversion tool to create man files"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("make/[^4.3]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/help2man/help2man-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"help2man-{self.version}")
        autotools.make()
        autotools.install()
