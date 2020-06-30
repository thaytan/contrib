import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class AutoconfArchiveConan(ConanFile):
    name = "autoconf-archive"
    version = tools.get_env("GIT_TAG", "2019.01.06")
    license = "GPL3"
    description = "A collection of freely re-usable Autoconf macros"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftpmirror.gnu.org/autoconf-archive/autoconf-archive-%s.tar.xz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
