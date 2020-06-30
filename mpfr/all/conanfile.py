import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class MpfrConan(ConanFile):
    name = "mpfr"
    version = tools.get_env("GIT_TAG", "4.0.2")
    settings = "os", "compiler", "arch"
    license = "LGPL"
    description = "Multiple-precision floating-point library"

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("make/[>=4.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gmp/[>=6.1.2]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/mpfr/mpfr-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
