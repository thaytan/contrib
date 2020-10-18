import os

from conans import *


class LibepoxyConan(ConanFile):
    description = "Library handling OpenGL function pointer management"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.51.2]",
    )
    requires = (
        "base/[^1.0.0]",
        "libx11/[^1.6.8]",
        "mesa/[^19.2.0]",
    )

    def source(self):
        tools.get(f"https://github.com/anholt/libepoxy/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled", "-Dglx=yes", "-Dx11=true", "-Dtests=false"]
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
        meson.install()
