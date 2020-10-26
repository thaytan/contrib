from build import *


class LibxauRecipe(Recipe):
    description = "X11 authorisation library"
    license = "MIT"
    build_requires = (
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
    )
    requires = ("xorgproto/[^2020.1]",)

    def source(self):
        self.get(f"https://xorg.freedesktop.org/releases/individual/lib/libXau-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
        ]
        self.autotools(args)
