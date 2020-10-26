from build import *


class LibeventRecipe(Recipe):
    description = "Event notification library https://libevent.org"
    license = "BSD-3-Clause"
    exports = "uninstall.patch"
    build_requires = (
        "env-generator/1.0.0",
        "cmake/3.15.3",
    )
    requires = (
        "base/[^1.0.0]",
        "openssl/1.1.1b",
        "zlib/[^1.2.11]",
    )

    def source(self):
        self.get(f"https://github.com/libevent/libevent/releases/download/release-{self.version}-stable/libevent-{self.version}-stable.tar.gz")
        self.patch("uninstall.patch")
