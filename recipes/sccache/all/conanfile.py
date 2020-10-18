from conans import *


class SccacheConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "rust/[^1.47.0]",
        "openssl1/[^1.1.1h]",
    )

    def source(self):
        tools.get(f"https://github.com/mozilla/sccache/archive/{self.version}.tar.gz")

    def build(self):
        self.run("cargo build --release", cwd=f"sccache-{self.version}")

    def package(self):
        self.copy(pattern="*/sccache", dst="bin", keep_path=False)

    def package_info(self):
        self.env_info.RUSTC_WRAPPER = "sccache"
