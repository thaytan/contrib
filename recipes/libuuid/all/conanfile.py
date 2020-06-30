from glob import glob
from os import path, remove

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibuuidConan(ConanFile):
    name = "libuuid"
    version = tools.get_env("GIT_TAG", "1.0.3")
    settings = "os", "compiler", "build_type", "arch"
    license = "BSD-3-Clause"
    description = "Portable uuid C library"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://netix.dl.sourceforge.net/project/libuuid/libuuid-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
