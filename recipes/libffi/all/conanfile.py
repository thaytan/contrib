from conans import *


class LibffiConan(ConanFile):
    description = "Portable foreign function interface library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("make/[^4.3]",)

    def source(self):
        tools.get(f"https://github.com/libffi/libffi/releases/download/v{self.version}/libffi-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-dependency-tracking",
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libffi-{self.version}", args)
        autotools.make()
        autotools.install()
