import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class MpcConan(ConanFile):
    description = "Library for the arithmetic of complex numbers with arbitrarily high precision"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/[^7.4.0]")
        self.build_requires("make/[^4.3]")

    def requirements(self):
        self.requires("mpfr/[^4.0.2]")

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/mpc/mpc-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
