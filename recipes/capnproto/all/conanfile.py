from conans import *


class CapNProtoConan(ConanFile):
    description = "Cap'n Proto serialization/RPC system"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://capnproto.org/capnproto-c++-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"capnproto-c++-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
