import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class TexinfoConan(ConanFile):
    name = "texinfo"
    version = tools.get_env("GIT_TAG", "6.6")
    settings = "os", "compiler", "build_type", "arch"
    license = "GPL3"
    description = "GNU documentation system for on-line information and printed output"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/pub/gnu/texinfo/texinfo-%s.tar.xz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.MAKEINFO = os.path.join(self.package_folder, "bin", "makeinfo")
        self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "share", "texinfo"))
        for mod in ["libintl-perl", "Text-Unidecode", "Unicode-EastAsianWidth"]:
            self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "share", "texinfo", "lib", mod, "lib"))
