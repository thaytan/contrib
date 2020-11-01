from build import *


class LibpngRecipe(Recipe):
    description = "A collection of routines used to create PNG format graphics files"
    license = "custom"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/1.0.0",
    )
    requires = ("zlib/[^1.2.11]",)

    def source(self):
        self.get(f"https://downloads.sourceforge.net/sourceforge/libpng/libpng-{self.version}.tar.xz")
