import os

from conans import *


class CurlConan(ConanFile):
    name = "curl"
    description = "An URL retrieval utility and library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cc/[^1.0.0]",
        "zlib/[^1.2.11]",
        "openssl/[^1.1.1b]",
    )

    def source(self):
        tools.get(f"https://curl.haxx.se/download/curl-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
