import os
from conans import *


class CairoConan(ConanFile):
    description = "2D graphics library with support for multiple output devices"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.51.2]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "glib/[^2.62.0]",
        "pixman/[^0.38.4]",
        "libxrender/[^0.9.10]",
        "libxext/[^1.3.4]",
        "fontconfig/[^2.13.1]",
        "zlib/[^1.2.11]",
        "libpng/[^1.6.37]",
    )

    def source(self)
        tools.get(f"https://github.com/centricular/cairo/archive/meson-{self.version}.tar.gz")

    def build(self):
        meson = Meson(self)
        args = [
            "-Dintrospection=enabled",
            "-Dfontconfig=enabled",
            "-Dzlib=enabled",
            "-Dpng=enabled",
        ]
        meson.configure(args, source_folder=f"pango-${self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
