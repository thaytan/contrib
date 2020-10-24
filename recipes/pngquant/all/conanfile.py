from conans import *


class PngquantConan(ConanFile):
    description = "Command-line utility to quantize PNGs down to 8-bit paletted PNGs"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/1.0.0",)
    requires = (
        "libpng/[^1.6.37]",
        "libimagequant/[^2.12.6]",
        "openmp/[^11.0.0]",
    )

    def source(self):
        tools.get(f"https://github.com/kornelski/pngquant/archive/{self.version}/pngquant-{self.version}.tar.gz")

    def build(self):
        args = [
            "--with-openmp",
        ]
        with tools.chdir(f"pngquant-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
