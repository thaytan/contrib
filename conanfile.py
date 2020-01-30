import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class MakeConan(ConanFile):
    name = "make"
    version = tools.get_env("GIT_TAG", "4.3")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "GNU make utility to maintain groups of programs"

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/7.4.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/make/make-{}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
