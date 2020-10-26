from build import *


class LibpthreadStubsRecipe(Recipe):
    description = "X11 client-side library"
    license = "MIT"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        self.get(f"https://xcb.freedesktop.org/dist/libpthread-stubs-{self.version}.tar.bz2")
