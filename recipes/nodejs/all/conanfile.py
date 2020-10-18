import os

from conans import *


class NodejsConan(ConanFile):
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
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
