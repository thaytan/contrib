import os

from conans import *


class NodejsConan(ConanFile):
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "autotools/[^1.0.0]",
        "python/[^3.7.4]",
    )
    requires = (
        "base/[^1.0.0]",
        "openssl/[^1.1.1b]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://github.com/nodejs/node/archive/v{self.version}.tar.gz")

    def build(self):
        args = ["--without-npm", "--shared-openssl", "--shared-zlib"]
        with tools.chdir(f"node-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
