from build import *


class LibxcursorRecipe(Recipe):
    description = "X cursor management library"
    license = "custom"
    build_requires = (
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = (
        "base/[^1.0.0]",
        "libxrender/[^0.9.10]",
        "libxfixes/[^5.0.3]",
    )

    def source(self):
        self.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXcursor-{self.version}.tar.gz")
