import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class TclConan(ConanFile):
    name = "tcl"
    version = tools.get_env("GIT_TAG", "8.6.10")
    description = "The Tcl scripting language"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://downloads.sourceforge.net/sourceforge/tcl/tcl%s-src.tar.gz"
            % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(
                os.path.join("%s%s" % (self.name, self.version), "unix")):
            autotools.configure()
            autotools.install()
