from conans import *


class Libtasn1Conan(ConanFile):
    description = "The ASN.1 library used in GNUTLS"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/libtasn1/libtasn1-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libtasn1-{self.version}", args)
        autotools.make()
        autotools.install()
