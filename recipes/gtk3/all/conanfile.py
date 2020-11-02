from build import *


class Gtk3Recipe(Recipe):
    description = "GObject-based multi-platform GUI toolkit"
    license = "LGPL-2.1"
    options = {
        "introspection": [True, False],
        "x11": [True, False],
    }
    default_options = (
        "introspection=True",
        "x11=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "gettext/[^0.21]",
    )
    requires = (
        "libepoxy/[^1.5.4]",
        "at-spi2-atk/[^2.38.0]",
        "gdk-pixbuf/[^2.40.0]",
        "pango/[^1.43.0]",
    )

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]",)

    def requirements(self):
        if self.options.x11:
            self.requires("libxkbcommon/[^1.0.1]")
            self.requires("libxrandr/[^1.5.2]")
            self.requires("libxi/[^1.7.1]")

    def source(self):
        self.get(f"https://github.com/GNOME/gtk/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "-Dwayland_backend=false",
        ]
        self.meson(args)
