import os

from conans import *


class GnutlsConan(ConanFile):
    description = "A library which provides a secure layer over a reliable transport layer"
    license = "custom", "FDL", "GPL", "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "gcc/[^7.4.0]",
        "make/[^4.3]",
    )
    requires = ("zlib/[^1.2.11]",)

    def source(self):
        tools.get("https://www.gnupg.org/ftp/gcrypt/gnutls/v3.6/gnutls-{}.tar.xz".format(self.version))

    def build(self):
        args = ["--with-zlib", "--disable-static", "--with-included-unistring"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
