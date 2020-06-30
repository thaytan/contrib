from conans import *

class PngquantConan(ConanFile):
    name = "pngquant"
    version = tools.get_env("GIT_TAG", "2.12.6")
    description = "Command-line utility to quantize PNGs down to 8-bit paletted PNGs"
    license = "BSD"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("autotools/1.0.0@%s/stable" % self.user)

    def requirements(self):
        self.requires("generators/1.0.0@%s/stable" % self.user)
        self.requires("libpng/[>=1.6.37]@%s/stable" % self.user)
        self.requires("libimagequant/[>=2.12.6]@%s/stable" % self.user)

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
