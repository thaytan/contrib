from build import *


class LibffiRecipe(Recipe):
    description = "Portable foreign function interface library"
    license = "MIT"
    build_requires = ("make/[^4.3]",)

    def source(self):
        self.get(f"https://github.com/libffi/libffi/releases/download/v{self.version}/libffi-{self.version}.tar.gz")
