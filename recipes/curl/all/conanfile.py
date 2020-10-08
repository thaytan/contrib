import os
from conans import *


class CurlConan(ConanFile):
    description = "An URL retrieval utility and library"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "clang/[^10.0.1]",
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "zlib/[^1.2.11]",
        "openssl/[^3.0.0-alpha6]",
    )
    requires = ("ca-certificates/[^20191127]",)

    def source(self):
        tools.get(f"https://curl.haxx.se/download/curl-{self.version}.tar.gz")

    def build(self):
        env = {
            "CFLAGS": os.environ["CFLAGS"] + "-ldl -lpthread",
        }
        args = ["--disable-shared"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"curl-{self.version}", args, vars=env)
        autotools.make()
        autotools.install()
