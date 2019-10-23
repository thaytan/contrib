import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class BisonConan(ConanFile):
    name = "bison"
    version = tools.get_env("GIT_TAG", "3.3")
    url = "https://gitlab.com/aivero/public/conan/conan" + name
    description = "Bison is a general-purpose parser generator"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("m4/[>=1.4.18]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/bison/bison-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.BISON_PKGDATADIR = os.path.join(
            self.package_folder, "share", "bison"
        )
