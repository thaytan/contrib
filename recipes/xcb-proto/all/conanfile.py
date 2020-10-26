from conans import *


class XcbProtoConan(ConanFile):
    description = "XML-XCB protocol descriptions"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        tools.get(f"https://xcb.freedesktop.org/dist/xcb-proto-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"xcb-proto-{self.version}")
        autotools.install()
