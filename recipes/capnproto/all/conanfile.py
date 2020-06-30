from conans import *


class CapNProtoConan(ConanFile):
    description = "Cap'n Proto serialization/RPC system"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("generators/1.0.0",)

    def source(self):
        tools.get("https://capnproto.org/capnproto-c++-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("capnproto-c++-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
