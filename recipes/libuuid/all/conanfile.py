from build import *


class LibuuidRecipe(Recipe):
    description = "Portable uuid C library"
    license = "BSD-3-Clause"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        self.get(f"https://netix.dl.sourceforge.net/project/libuuid/libuuid-{self.version}.tar.gz")
