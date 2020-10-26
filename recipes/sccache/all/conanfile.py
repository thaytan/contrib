from build import *


class SccacheRecipe(Recipe):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    build_requires = (
        "rust/[^1.47.0]",
        "openssl1/[^1.1.1h]",
    )

    def source(self):
        self.get(f"https://github.com/mozilla/sccache/archive/{self.version}.tar.gz")

    def build(self):
        self.run("cargo build --release", cwd=f"sccache-{self.version}")

    def package(self):
        self.copy(pattern="*/sccache", dst="bin", keep_path=False)

    def package_info(self):
        self.env_info.RUSTC_WRAPPER = "sccache"
