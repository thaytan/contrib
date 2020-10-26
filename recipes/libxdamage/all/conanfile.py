from build import *


class LibxdamageRecipe(Recipe):
    description = "X11 damaged region extension library"
    license = "custom"
    build_requires = ("autotools/[^1.0.0]",)
    requires = ("libxfixes/[^5.0.3]",)

    def source(self):
        self.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXdamage-{self.version}.tar.gz")
