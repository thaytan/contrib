import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GccGmpConan(ConanFile):
    name = "gcc-gmp"
    version = tools.get_env("GIT_TAG", "6.1.2")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "A free library for arbitrary precision arithmetic"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("bootstrap-gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("m4/[>=1.4.18]@%s/stable" % self.user)
        self.build_requires("make/[>=4.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gmplib.org/download/gmp/gmp-%s.tar.xz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("gmp-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
