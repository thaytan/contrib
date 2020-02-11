from glob import glob
from os import path, remove

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class FreetypeConan(ConanFile):
    name = "freetype"
    version = tools.get_env("GIT_TAG", "2.10.1")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "FreeType is a software library to render fonts"
    license = "GPL2"
    settings = "os", "arch", "compiler", "build_type"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("harfbuzz/2.6.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://git.savannah.gnu.org/cgit/freetype/freetype2.git/snapshot/freetype2-VER-%s.tar.gz" % self.version.replace(".", "-"))

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("freetype2-VER-" + self.version.replace(".", "-")):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
