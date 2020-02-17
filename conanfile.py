import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class RenderprotoConan(ConanFile):
    name = "renderproto"
    version = tools.get_env("GIT_TAG", "0.11.1")
    description = "X11 Render extension wire protocol"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/proto/renderproto-%s.tar.gz" % self.version)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            os.remove("config.guess")
            os.remove("config.sub")
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD", "config.guess")
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD", "config.sub")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
