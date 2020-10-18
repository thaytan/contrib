import os
from conans import *


class PixmanConan(ConanFile):
    description = "Image processing and manipulation library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.51.2]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/pixman-{self.version}.tar.bz2")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(args, source_folder=f"name-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
