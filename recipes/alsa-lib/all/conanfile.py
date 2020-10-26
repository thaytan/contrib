from build import *


class AlsaLibRecipe(Recipe):
    description = "An alternative implementation of Linux sound support"
    license = "LGPL2.1"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        self.get(f"https://www.alsa-project.org/files/pub/lib/alsa-lib-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-static",
        ]
        self.autotools(args)
