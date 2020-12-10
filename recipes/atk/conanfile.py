from build import *


class AtkRecipe(Recipe):
    description = "GObject-based multi-platform GUI toolkit"
    license = "LGPL-2.1"
    options = {
        "introspection": [True, False],
    }
    default_options = ("introspection=True",)
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "gettext/[^0.21]",
    )
    requires = ("glib/[^2.66.1]",)

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]",)

    def source(self):
        version = self.version.replace(".", "_")
        self.get(f"https://gitlab.gnome.org/GNOME/atk/-/archive/ATK_{version}/atk-ATK_{version}.tar.bz2")
