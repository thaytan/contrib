from build import *


class LibsrtpRecipe(Recipe):
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    license = "BSD"
    build_requires = (
        "cc/[^1.0.0]", 
        "cmake/[^3.18.4]",
    )
    exports_sources = (
        "libsrtp2.pc",
    )

    def source(self):
        self.get(f"https://github.com/cisco/libsrtp/archive/v{self.version}.tar.gz")

    def package(self):
        self.copy("libsrtp2.pc", dst="lib/pkgconfig")