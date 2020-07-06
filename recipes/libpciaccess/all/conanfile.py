from conans import *


class LibPciAccessConan(ConanFile):
    description = "Generic PCI access library"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "env-generator/1.0.0",
        "xorg-util-macros/[^1.19.1]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/lib/libpciaccess-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure(args=args)
            autotools.install()
