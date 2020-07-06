import os

from conans import *


class GnutlsConan(ConanFile):
    description = "A library which provides a secure layer over a reliable transport layer"
    license = "custom", "FDL", "GPL", "LGPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )
    requires = (
        "base/[^1.0.0]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://www.gnupg.org/ftp/gcrypt/gnutls/v3.6/gnutls-{self.version}.tar.xz")

    def build(self):
        args = ["--with-zlib", "--disable-static", "--with-included-unistring"]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
