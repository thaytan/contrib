from conans import *


class GnutlsConan(ConanFile):
    description = "A library which provides a secure layer over a reliable transport layer"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "clang/[^10.0.1]",
        "make/[^4.3]",
        "zlib/[^1.2.11]",
        "pkgconf/[^1.7.3]",
    )
    requires = (
        "nettle/[^3.6]",
        "libtasn1/[^4.16.0]",
    )

    def source(self):
        tools.get(f"https://www.gnupg.org/ftp/gcrypt/gnutls/v3.6/gnutls-{self.version}.tar.xz")

    def build(self):
        args = [
            "--with-zlib",
            "--disable-shared",
            "--with-included-unistring",
            "--without-p11-kit",
            "--disable-tests",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"gnutls-{self.version}", args)
        autotools.make()
        autotools.install()
