from conans import *


class LibsrtpConan(ConanFile):
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get(f"https://github.com/cisco/libsrtp/archive/v{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libsrtp-{self.version}")
        autotools.make()
        autotools.install()
