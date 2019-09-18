from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.util import files
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.6.1"
    except:
        return None

class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    version = get_version()
    license = "Old MIT"
    description = "HarfBuzz text shaping engine"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def build_requirements(self):
        self.build_requires("freetype-no-harfbuzz/2.10.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/harfbuzz/harfbuzz/archive/%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name , self.version)):
            self.run("./autogen.sh")
            autotools.configure()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
