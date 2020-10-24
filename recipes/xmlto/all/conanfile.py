from conans import *


class XmltoConan(ConanFile):
    description = "Convert xml to many other formats"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)
    requires = ("libxslt/[^1.1.34]",)

    def source(self):
        tools.get(f"https://releases.pagure.org/xmlto/xmlto-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-static",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"xmlto-{self.version}", args)
        autotools.make()
        autotools.install()
