import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class NodejsConan(ConanFile):
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("autotools/[^1.0.0]")
        self.build_requires("python/[^3.7.4]")

    def requirements(self):
        self.requires("generators/1.0.0")
        self.requires("openssl/[^1.1.1b]")
        self.requires("zlib/[^1.2.11]")

    def source(self):
        tools.get("https://github.com/nodejs/node/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--without-npm", "--shared-openssl", "--shared-zlib"]
        with tools.chdir("node-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
