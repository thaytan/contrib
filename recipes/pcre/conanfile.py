from build import *


class Pcre(Recipe):
    description = "A library that implements Perl 5-style regular expressions"
    license = "BSD"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
    )
    requires = (
        "readline/[^8.1]",
        "zlib/[^1.2.11]",
        "bzip2/[^1.0.8]",
    )

    def source(self):
        self.get(f"https://sourceforge.net/projects/pcre/files/pcre/{self.version}/pcre-{self.version}.tar.bz2")