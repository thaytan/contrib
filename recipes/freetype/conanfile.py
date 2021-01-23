from build import *


class FreetypeRecipe(Recipe):
    description = "FreeType is a software library to render fonts"
    license = "GPL"
    options = {"harfbuzz": [True, False]}
    default_options = ("harfbuzz=True",)
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def configure(self):
        # Avoid circular requirement
        self.options["freetype-no-harfbuzz"].harfbuzz = False

    def requirements(self):
        if self.options.harfbuzz:
            self.requires("harfbuzz/[^2.7.2]")
            # Using harfbuzz requires freetype
            self.requires(f"freetype-no-harfbuzz/[^{self.version}]", "private")
            self.requires("zlib/[^1.2.11]")
        else:
            self.requires("zlib/[^1.2.11]", "private")

    def source(self):
        self.get(f"https://download-mirror.savannah.gnu.org/releases/freetype/freetype-{self.version}.tar.xz")

    def build(self):
        self.autotools()
