from build import *


class IslRecipe(Recipe):
    description = "Library for manipulating sets and relations of integer points bounded by linear constraints"
    license = "MIT"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )
    requires = ("gmp/[^6.2.0]",)

    def source(self):
        self.get(f"http://isl.gforge.inria.fr/isl-{self.version}.tar.xz")
