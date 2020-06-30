from conans import *


class ZlibConan(ConanFile):
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library " "(Also Free, Not to Mention Unencumbered by Patents)"
    license = "Zlib"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"https://github.com/madler/zlib/archive/v{self.version}.tar.gz")

    def build(self):
        args = ["--enable-shared"]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
