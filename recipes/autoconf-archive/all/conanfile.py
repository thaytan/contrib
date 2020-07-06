import os

from conans import *


class AutoconfArchiveConan(ConanFile):
    name = "autoconf-archive"
    description = "A collection of freely re-usable Autoconf macros"
    license = "GPL3"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("autoconf/[^2.69]",)

    def source(self):
        tools.get(f"https://ftpmirror.gnu.org/autoconf-archive/autoconf-archive-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
