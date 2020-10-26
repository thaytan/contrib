from build import *


class AutoconfArchiveRecipe(Recipe):
    description = "A collection of freely re-usable Autoconf macros"
    license = "GPL3"
    build_requires = ("autoconf/[^2.69]",)

    def source(self):
        self.get(f"https://ftpmirror.gnu.org/autoconf-archive/autoconf-archive-{self.version}.tar.xz")
