from build import *


class GLibRecipe(Recipe):
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    license = "LGPL2.1"
    build_requires = ("meson/[^0.55.3]",)
    requires = (
        "libffi/[^3.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        self.get(f"https://github.com/GNOME/glib/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "-Dman=False",
            "-Dgtk_doc=False",
            "-Dinternal_pcre=False",
        ]
        self.meson(args)
