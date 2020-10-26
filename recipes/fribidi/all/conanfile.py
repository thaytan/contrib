import os
from conans import *


class FribidiConan(ConanFile):
    description = "The Free Implementation of the Unicode Bidirectional Algorithm"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("meson/[^0.55.3]",)

    def source(self):
        tools.get(f"https://github.com/fribidi/fribidi/archive/v{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled", "-Ddocs=false"]
        meson = Meson(self)
        meson.configure(args, source_folder=f"fribidi-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
