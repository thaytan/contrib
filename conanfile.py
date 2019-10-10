import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.16.1"
    except:
        return None


class AutomakeConan(ConanFile):
    name = "automake"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "A GNU tool for automatically creating Makefiles"
    exports = "automake-include-fix.patch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/automake/automake-%s.tar.gz" % self.version)
        tools.patch(
            patch_file="automake-include-fix.patch",
            base_path="%s-%s" % (self.name, self.version),
        )

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.AUTOMAKE = os.path.join(self.package_folder, "bin", "automake")
        self.env_info.AUTOMAKE_DIR = os.path.join(self.package_folder, "share")
        self.env_info.AUTOMAKE_LIBDIR = os.path.join(
            self.package_folder, "share", "automake-1.16"
        )
        self.env_info.ACLOCAL = os.path.join(self.package_folder, "bin", "aclocal")
        self.env_info.ACLOCAL_DIR = os.path.join(self.package_folder, "share")
        self.env_info.ACLOCAL_PATH.append(
            os.path.join(self.package_folder, "share", "aclocal-1.16")
        )
        self.env_info.PERL5LIB.append(
            os.path.join(self.package_folder, "share", "automake-1.16")
        )
