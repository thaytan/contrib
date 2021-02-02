from build import *


class LibuuidRecipe(Recipe):
    description = "Portable uuid C library"
    license = "BSD"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def source(self):
        self.get(f"https://netix.dl.sourceforge.net/project/libuuid/libuuid-{self.version}.tar.gz")
