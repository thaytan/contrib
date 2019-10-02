from glob import glob
from os import path, remove

from conans import AutoToolsBuildEnvironment, ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.13.1"
    except:
        return None

class FontconfigConan(ConanFile):
    name = "fontconfig"
    version = get_version()
    license = "Old MIT"
    description = "A library for configuring and customizing font access"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("gperf/[>=3.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("freetype/[>=2.10.1]@%s/stable" % self.user)
        self.requires("libuuid/[>=1.0.3]@%s/stable" % self.user)
        self.requires("expat/[>=2.2.7]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/fontconfig/fontconfig/-/archive/{0}/fontconfig-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name , self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
