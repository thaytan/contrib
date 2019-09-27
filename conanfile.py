from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "3.3"
    except:
        return None

class BisonConan(ConanFile):
    name = "bison"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-bison"
    description = "Bison is a general-purpose parser generator"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/bison/bison-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.BISON_PKGDATADIR = os.path.join(self.package_folder, "share", "bison")
