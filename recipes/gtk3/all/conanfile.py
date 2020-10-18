import os

from conans import *


class Gtk3Conan(ConanFile):
    description = "GObject-based multi-platform GUI toolkit"
    license = "LGPL-2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {
        "introspection": [True, False],
        "x11": [True, False],
    }
    default_options = (
        "introspection=True",
        "x11=True",
    )
    build_requires = (
        "meson/[^0.51.2]",
        "gettext/[^0.20.1]",
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]",)
    )
    requires = (
        "glib/[^2.62.0]",
        "cairo/[^1.16.0]",
        "libepoxy/[^1.5.3]",
        "atk/[^2.35.1]",
        "at-spi2-atk/[^2.34.0]",
        "gdk-pixbuf/[^2.38.2]",
        "pango/[^1.43.0]",
        if self.options.x11:
            "libx11/[^1.6.8]",
            "libxkbcommon/[^0.8.4]",
            "libxrandr/[^1.5.2]",
            "libxi/[^1.7.1]",
    )

    def source(self):
        tools.get(f"https://github.com/GNOME/gtk/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "--wrap-mode=nofallback",
            "-Dwayland_backend=false",
        ]
        meson = Meson(self)
        meson.configure(source_folder="gtk-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
