import os
from os import environ, path, pathsep

from conans import *


class GdkPixbufConan(ConanFile):
    description = "An image loading library"
    license = "LGPL-2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.51.2]",
        "gobject-introspection/[^1.59.3]",
        "gettext/[^0.20.1]",
        "imagemagick/7.0.9.25",
    )
    requires = (
        "glib/[^2.62.0]",
        "libx11/[^1.6.8]",
        "libpng/[^1.6.37]",
        "shared-mime-info/[^1.14]",
    )

    def source(self):
        tools.get(f"https://github.com/GNOME/gdk-pixbuf/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "--wrap-mode=nofallback",
            "-Dinstalled_tests=false",
            "-Drelocatable=true",
        ]
        self.run(f'convert gdk-pixbuf-{self.version}/tests/icc-profile.png +profile "*" gdk-pixbuf-{self.version}/tests/icc-profile.png')
        with tools.environment_append({"PATH": environ["PATH"] + pathsep + path.join(self.build_folder, "gdk-pixbuf")}):
            meson = Meson(self)
            meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
            meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
