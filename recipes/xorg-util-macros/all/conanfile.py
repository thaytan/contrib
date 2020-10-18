import os

from conans import *


class LibXorgUtilMacrosConan(ConanFile):
    description = "X.Org Autotools macros"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/releases/individual/util/util-macros-{self.version}.tar.gz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(f"util-macros-{self.version}"):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
