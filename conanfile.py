from conans import ConanFile, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.9.0"
    except:
        return None

class NinjaConan(ConanFile):
    name = "ninja"
    version = get_version()
    license = "Apache"
    description = "Small build system with a focus on speed"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/ninja-build/ninja/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name , self.version)):
            self.run("python2 configure.py --bootstrap")

    def package(self):
        self.copy(os.path.join("%s-%s" % (self.name, self.version), "ninja"), "bin")
        if self.settings.build_type == "Debug":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")

    def package_info(self):
        self.cpp_info.srcdirs.append("src")
