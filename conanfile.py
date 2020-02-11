import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibeditConan(ConanFile):
    name = "libedit"
    version = tools.get_env("GIT_TAG", "20190324-3.1")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "Zlib"
    description = "System V Release 4.0 curses emulation library"
    settings = "os", "arch", "compiler", "build_type"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("ncurses/[>=6.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://thrysoee.dk/editline/libedit-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
