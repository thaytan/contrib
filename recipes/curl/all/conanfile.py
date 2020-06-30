import os

from conans import *


class CurlConan(ConanFile):
    description = "An URL retrieval utility and library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
        "zlib/[^1.2.11]",
        "openssl/[^1.1.1b]",
    )

    def source(self):
        tools.get("https://curl.haxx.se/download/curl-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
