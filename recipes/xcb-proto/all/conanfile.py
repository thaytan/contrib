from conans import *


class XcbProtoConan(ConanFile):
    description = "XML-XCB protocol descriptions"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "pkgconf/[^1.6.3]",
    )

    def source(self):
        tools.get("https://xcb.freedesktop.org/dist/xcb-proto-%s.tar.bz2" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
