from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.20.1"
    except:
        return None

class GettextConan(ConanFile):
    name = "gettext"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-" + name
    license = "GPL"
    description = "GNU internationalization library"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/pub/gnu/gettext/gettext-%s.tar.gz" % self.version)

    def build(self):
        args = []
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
