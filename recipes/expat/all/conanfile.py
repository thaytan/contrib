from build import *


class ExpatRecipe(Recipe):
    description = "An XML parser library"
    license = "MIT"
    build_requires = ("make/[^4.3]",)

    def source(self):
        self.get(f"https://github.com/libexpat/libexpat/releases/download/R_{self.version.replace('.', '_')}/expat-{self.version}.tar.bz2")
