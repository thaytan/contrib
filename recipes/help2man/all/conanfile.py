from conans import *


class Help2ManConan(ConanFile):
    description = "Conversion tool to create man files"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("cc/[^1.0.0]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/help2man/help2man-{self.version}.tar.xz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
