from build import *


class MpfrRecipe(Recipe):
    description = "Multiple-precision floating-point library"
    license = "LGPL"
    build_requires = (
        "make/[^4.3]",
        "gmp/[^6.2.0]",
    )

    def source(self):
        self.get(f"https://ftp.gnu.org/gnu/mpfr/mpfr-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        self.autotools(args)
