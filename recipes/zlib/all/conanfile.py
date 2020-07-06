from conans import *


class ZlibConan(ConanFile):
    name = "zlib"
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library " "(Also Free, Not to Mention Unencumbered by Patents)"
    license = "Zlib"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("clang-bootstrap/[^10.0.0]",)
    requires = ("musl/[^1.2.0]",)

    def source(self):
        tools.get(f"https://github.com/madler/zlib/archive/v{self.version}.tar.gz")

    def build(self):
        args = ["--enable-shared"]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
