from build import *


class SccacheRecipe(RustRecipe):
    description = "Development and debugging tools for GStreamer"
    license = "Apache"
    build_requires = (
        "rustc/[^1.47.0]",
        "pkgconf/[^1.7.3]",
    )
    requires = ("openssl1/[^1.1.1h]", "libssl/[^1.0.0]")

    def source(self):
        self.get(f"https://github.com/mozilla/sccache/archive/{self.version}.tar.gz")

    def package_info(self):
        self.env_info.RUSTC_WRAPPER = "sccache"
