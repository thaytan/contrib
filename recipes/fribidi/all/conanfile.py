from build import *


class FribidiRecipe(Recipe):
    description = "The Free Implementation of the Unicode Bidirectional Algorithm"
    license = "LGPL"
    build_requires = ("meson/[^0.55.3]",)

    def source(self):
        self.get(f"https://github.com/fribidi/fribidi/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "-Ddocs=false",
        ]
        self.meson(args)
