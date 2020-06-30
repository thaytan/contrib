import os

from conans import *


class NodejsConan(ConanFile):
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "autotools/[^1.0.0]",
        "python/[^3.7.4]",
    )
    requires = (
        "generators/1.0.0",
        "openssl/[^1.1.1b]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get("https://github.com/nodejs/node/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--without-npm", "--shared-openssl", "--shared-zlib"]
        with tools.chdir("node-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
