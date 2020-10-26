from build import *


class LibxcbRecipe(Recipe):
    description = "X11 client-side library"
    license = "MIT"
    build_requires = (
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "xcb-proto/[^1.13]",
        "libpthread-stubs/[^0.4]",
    )
    requires = ("libxau/[^1.0.9]",)

    def source(self):
        self.get(f"https://xcb.freedesktop.org/dist/libxcb-{self.version}.tar.xz")

    def build(self):
        args = ["--disable-static"]
        self.autotools(args)
