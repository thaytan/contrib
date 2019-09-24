from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.69"
    except:
        return None

class AutoconfConan(ConanFile):
    name = "autoconf"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL3"
    description = "A GNU tool for automatically configuring source code"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/0.1@%s/stable" % self.user)

    def requirements(self):
        self.requires("m4/1.4.18@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/autoconf/autoconf-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.srcdirs.append("src")
        self.env_info.AUTOM4TE = os.path.join(self.package_folder, "bin", "autom4te")
