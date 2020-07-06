from conans import *


class XtransConan(ConanFile):
    name = "xtrans"
    description = "X transport library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/xtrans-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()
