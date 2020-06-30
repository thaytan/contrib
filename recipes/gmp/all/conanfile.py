import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GmpConan\(ConanFile\):
    description = "A free library for arbitrary precision arithmetic"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("bootstrap-gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("m4/[>=1.4.18]@%s/stable" % self.user)
        self.build_requires("make/[>=4.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gmplib.org/download/gmp/gmp-%s.tar.xz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
