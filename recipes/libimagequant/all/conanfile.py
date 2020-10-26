import os
from conans import *


class LibimagequantConan(ConanFile):
    description = "Library for high-quality conversion of RGBA images to 8-bit indexed-color (palette) images"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/1.0.0",
        "openmp/[^11.0.0]",
    )

    def source(self):
        tools.get(f"https://github.com/ImageOptim/libimagequant/archive/{self.version}/libimagequant-{self.version}.tar.gz")

    def build(self):
        env = {
            "DESTDIR": self.package_folder,
        }
        args = [
            "--with-openmp",
        ]
        with tools.environment_append(env), tools.chdir(f"libimagequant-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
        os.remove(os.path.join(self.package_folder, "lib", "libimagequant.a"))
