from conans import *


class WgetConan(ConanFile):
    description = "Network utility to retrieve files from the Web"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "nettle/[^3.6]",
        "libtasn1/[^4.16.0]",
    )
    requires = ("gnutls/[^3.6.15]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/wget/wget-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"wget-{self.version}")
        autotools.make()
        autotools.install()
