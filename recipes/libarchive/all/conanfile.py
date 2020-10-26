from build import *


class LibarchiveRecipe(Recipe):
    description = "Multi-format archive and compression library"
    license = "BSD"
    build_requires = (
        "autotools/[^1.0.0]",
        "expat/[^2.2.7]",
        "zlib/[^1.2.11]",
        "xz/[^5.2.5]",
        "bzip2/[^1.0.8]",
    )
    requires = ("openssl1/[^1.1.1h]",)

    def source(self):
        self.get(f"https://github.com/libarchive/libarchive/releases/download/v{self.version}/libarchive-{self.version}.tar.xz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        self.autotools(args)
