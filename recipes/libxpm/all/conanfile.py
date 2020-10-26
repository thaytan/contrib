from build import *


class LibxpmRecipe(Recipe):
    description = "X11 pixmap library"
    license = "custom"
    build_requires = (
        "autotools/[^1.0.0]",
        "xorg-util-macros/[^1.19.1]",
    )
    requires = (
        "base/[^1.0.0]",
        "libx11/[^1.6.8]",
        "libxext/[^1.3.4]",
    )

    def source(self):
        self.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXpm-{self.version}.tar.gz")
