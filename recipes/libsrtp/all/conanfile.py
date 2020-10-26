from build import *


class LibsrtpRecipe(Recipe):
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    license = "BSD"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        self.get(f"https://github.com/cisco/libsrtp/archive/v{self.version}.tar.gz")
