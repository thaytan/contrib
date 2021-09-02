from build import *


class GLibRecipe(Recipe):
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    license = "LGPL"
    build_requires = ("cc/[^1.0.0]", "meson/[>=0.55.3]")
    requires = (
        "libffi/[^3.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        self.get(f"https://gitlab.gnome.org/GNOME/glib/-/archive/{self.version}/glib-{self.version}.tar.gz")

    def build(self):
        opts = {
            "man": False,
            "gtk_doc": False,
            "internal_pcre": False,
        }
        self.meson(opts)
