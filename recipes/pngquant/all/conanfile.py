from conans import *


class PngquantConan(ConanFile):
    name = "pngquant"
    description = "Command-line utility to quantize PNGs down to 8-bit paletted PNGs"
    license = "BSD"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("autotools/1.0.0",)
    requires = (
        "base/[^1.0.0]",
        "libpng/[^1.6.37]",
        "libimagequant/[^2.12.6]",
    )

    def source(self):
        tools.get(f"https://github.com/kornelski/pngquant/archive/{self.version}/pngquant-{self.version}.tar.gz")

    def build(self):
        args = [
            "--with-openmp",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
