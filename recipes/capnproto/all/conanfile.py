from conans import *


class CapNProtoConan(ConanFile):
    description = "Cap'n Proto serialization/RPC system"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://capnproto.org/capnproto-c++-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"capnproto-c++-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
