from conans import *


class LibSrtpConan(ConanFile):
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    license = "BSD"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/cisco/libsrtp/archive/v{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make(args=["shared_library"])
            autotools.install()
