import os

from conans import *


class TexinfoConan(ConanFile):
    description = "GNU documentation system for on-line information and printed output"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "clang/[^10.0.1]",
        "make/[^4.3]",
        "perl/[^5.30.0]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/texinfo/texinfo-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"texinfo-{self.version}")
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.MAKEINFO = os.path.join(self.package_folder, "bin", "makeinfo")
        self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "share", "texinfo"))
        for mod in ["libintl-perl", "Text-Unidecode", "Unicode-EastAsianWidth"]:
            self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "share", "texinfo", "lib", mod, "lib"))
