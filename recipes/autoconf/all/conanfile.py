import os

from conans import *


class AutoconfConan(ConanFile):
    description = "A GNU tool for automatically configuring source code"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    exports = "m4-include.patch"
    requires = (
        "m4/[^1.4.18]",
        "make/[^4.3]",
        "perl/[^5.30.0]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/autoconf/autoconf-{self.version}.tar.gz")
        tools.patch(patch_file="m4-include.patch", base_path=f"{self.name}-{self.version}")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"autoconf-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.AUTOCONF = os.path.join(self.package_folder, "bin", "autoconf")
        self.env_info.AUTOHEADER = os.path.join(self.package_folder, "bin", "autoheader")
        self.env_info.AUTOM4TE = os.path.join(self.package_folder, "bin", "autom4te")
        self.env_info.AC_MACRODIR = os.path.join(self.package_folder, "share", "autoconf")
        self.env_info.autom4te_perllibdir = os.path.join(self.package_folder, "share", "autoconf")
