from build import *


class PangoRecipe(Recipe):
    description = "A library for layout and rendering of text"
    license = "GPL"
    build_requires = (
        "meson/[^0.55.3]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "fribidi/[^1.0.5]",
        "cairo/[^1.17.2]",
    )

    def source(self):
        self.get(f"https://github.com/GNOME/pango/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "-Dfontconfig=enabled",
            "-Dfreetype=enabled",
            "-Dcairo=enabled",
        ]
        self.meson(args)
