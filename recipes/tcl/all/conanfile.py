import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class TclConan(ConanFile):
    name = "tcl"
    description = "The Tcl scripting language"
    license = "custom"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
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
