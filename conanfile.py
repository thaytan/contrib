import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class MpcConan(ConanFile):
    name = "mpc"
    version = tools.get_env("GIT_TAG", "1.1.0")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL"
    description = "Library for the arithmetic of complex numbers with arbitrarily high precision"

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("make/[>=4.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gmp/[>=6.1.2]@%s/stable" % self.user)

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
