import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GnutlsConan\(ConanFile\):
    description = "A library which provides a secure layer over a reliable transport layer"
    license = "custom", "FDL", "GPL", "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("make/[>=4.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)

    def source(self):
        tools.get("https://www.gnupg.org/ftp/gcrypt/gnutls/v3.6/gnutls-{}.tar.xz".format(self.version))

    def build(self):
        args = ["--with-zlib", "--disable-static", "--with-included-unistring"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
