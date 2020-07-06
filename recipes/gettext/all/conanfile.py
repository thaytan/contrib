from glob import glob
from os import path, remove, symlink

from conans import *


class GettextConan(ConanFile):
    name = "gettext"
    description = "GNU internationalization library"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    license = "GPL"
    build_requires = ("cc/[^1.0.0]",)

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/gettext/gettext-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
        symlink("preloadable_libintl.so", path.join(self.package_folder, "lib", "libpreloadable_libintl.so"))
        symlink("preloadable_libintl.so", path.join(self.package_folder, "lib", "libgnuintl.so.8"))

    def package_info(self):
        self.env_info.gettext_datadir.append(path.join(self.package_folder, "share", "gettext"))
