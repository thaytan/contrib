from conans import *


class ExpatConan(ConanFile):
    description = "An XML parser library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("make/[^4.3]",)

    def source(self):
        tools.get(f"https://github.com/libexpat/libexpat/releases/download/R_{self.version.replace('.', '_')}/expat-{self.version}.tar.bz2")

    def build(self):
        args = ["--disable-shared"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"expat-{self.version}", args)
        autotools.install()
