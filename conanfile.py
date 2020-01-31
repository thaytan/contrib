import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class IslConan(ConanFile):
    name = "isl"
    version = tools.get_env("GIT_TAG", "0.22.1")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = "Library for manipulating sets and relations of integer points bounded by linear constraints"

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/[>=7.4.0]@%s/stable" % self.user)

    def source(self):
        tools.get("http://isl.gforge.inria.fr/isl-%s.tar.xz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")
