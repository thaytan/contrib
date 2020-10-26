from build import *


class MpcRecipe(Recipe):
    description = "Library for the arithmetic of complex numbers with arbitrarily high precision"
    license = "LGPL"
    build_requires = (
        "make/[^4.3]",
        "mpfr/[^4.1.0]",
        "gmp/[^6.2.0]",
    )

    def source(self):
        self.get(f"https://ftp.gnu.org/gnu/mpc/mpc-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        self.autotools(args)
