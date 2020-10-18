from conans import *


class NettleConan(ConanFile):
    description = "A low-level cryptographic library"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )
    requires = ("gmp/[^6.2.0]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/nettle/nettle-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"nettle-{self.version}", args)
        autotools.make()
        autotools.install()
