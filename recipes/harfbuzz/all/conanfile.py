from build import *


class HarfbuzzRecipe(Recipe):
    description = "HarfBuzz text shaping engine"
    license = "MIT"
    build_requires = (
        "meson/[^0.55.3]",
        "freetype/[^2.10.3]",
        "gobject-introspection/[^1.66.1]",
    )

    def configure(self):
        # Avoid circular requirement
        self.options["freetype"].harfbuzz = False

    def source(self):
        self.get(f"https://github.com/harfbuzz/harfbuzz/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "-Dfreetype=enabled",
            "-Dgobject=enabled",
            "-Dintrospection=enabled",
        ]
        self.meson(args)
