from conans import *


class XcbProtoConan(ConanFile):
    description = "XML-XCB protocol descriptions"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("pkgconf/[^1.6.3]")

    def source(self):
        tools.get("https://xcb.freedesktop.org/dist/xcb-proto-%s.tar.bz2" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
