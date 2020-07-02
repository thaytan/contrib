from conans import *


class XcbProtoConan(ConanFile):
    description = "XML-XCB protocol descriptions"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = ("pkgconf/[^1.6.3]",)

    def source(self):
        tools.get(f"https://xcb.freedesktop.org/dist/xcb-proto-{self.version}.tar.bz2")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()
