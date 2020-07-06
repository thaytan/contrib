from conans import *


class LibunwindBoostrapConan(ConanFile):
    name = "libunwind-bootstrap"
    description = "Portable and efficient C programming interface (API) to determine the call-chain of a programs"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://download.savannah.gnu.org/releases/libunwind/libunwind-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir(f"libunwind-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
