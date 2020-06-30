import os

from conans import *


class AutoconfConan(ConanFile):
    description = "A GNU tool for automatically configuring source code"
    license = "GPL3"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports = "m4-include.patch"
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
    )
    requires = ("m4/[^1.4.18]",)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/autoconf/autoconf-%s.tar.gz" % self.version)
        tools.patch(patch_file="m4-include.patch", base_path="%s-%s" % (self.name, self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.AUTOCONF = os.path.join(self.package_folder, "bin", "autoconf")
        self.env_info.AUTOHEADER = os.path.join(self.package_folder, "bin", "autoheader")
        self.env_info.AUTOM4TE = os.path.join(self.package_folder, "bin", "autom4te")
        self.env_info.AC_MACRODIR = os.path.join(self.package_folder, "share", "autoconf")
        self.env_info.autom4te_perllibdir = os.path.join(self.package_folder, "share", "autoconf")
