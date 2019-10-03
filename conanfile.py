import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2019.01.06"
    except:
        return None

class AutoconfArchiveConan(ConanFile):
    name = "autoconf-archive"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL3"
    description = "A collection of freely re-usable Autoconf macros"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftpmirror.gnu.org/autoconf-archive/autoconf-archive-%s.tar.xz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
