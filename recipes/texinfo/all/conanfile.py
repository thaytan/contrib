import os

from conans import *


class TexinfoConan(ConanFile):
    description = "GNU documentation system for on-line information and printed output"
    license = "GPL3"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/texinfo/texinfo-{self.version}.tar.xz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.MAKEINFO = os.path.join(self.package_folder, "bin", "makeinfo")
        self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "share", "texinfo"))
        for mod in ["libintl-perl", "Text-Unidecode", "Unicode-EastAsianWidth"]:
            self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "share", "texinfo", "lib", mod, "lib"))
