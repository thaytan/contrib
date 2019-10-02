from glob import glob
from os import path, remove

from conans import AutoToolsBuildEnvironment, ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.0.3"
    except:
        return None

class LibuuidConan(ConanFile):
    name = "libuuid"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD-3-Clause"
    description = "Portable uuid C library"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://netix.dl.sourceforge.net/project/libuuid/libuuid-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static",]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
