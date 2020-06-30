import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ReadlineConan(ConanFile):
    description = "GNU readline library"
    license = "GPL-3.0-or-later"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[^7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("ncurses/[^6.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/readline/readline-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
