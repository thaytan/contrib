import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ItstoolConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    license = "GPL3"
    description = "XML to PO and back again"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxml2/[>=2.9.9]@%s/stable" % self.user)
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/itstool/itstool/archive/%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
