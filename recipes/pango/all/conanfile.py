import os

from conans import *


class PangoConan(ConanFile):
    description = "A library for layout and rendering of text"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "fribidi/[^1.0.5]",
        "cairo/[^1.17.2]",
        "harfbuzz/[^2.6.1]",
    )

    def source(self):
        tools.get(f"https://github.com/GNOME/pango/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dfontconfig=enabled",
            "-Dfreetype=enabled",
            "-Dcairo=enabled",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"pango-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
