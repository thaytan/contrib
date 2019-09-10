from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.util import files
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.40.1"
    except:
        return None

class GraphvizConan(ConanFile):
    version = get_version()
    name = "graphviz"
    license = "https://gitlab.com/graphviz/graphviz/blob/master/LICENSE"
    description = "Graph Visualization Tools"
    url = "https://gitlab.com/graphviz/graphviz"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("flex/2.6.4@%s/stable" % self.user, private=True)
        self.requires("bison/3.3@%s/stable" % self.user, private=True)

    def source(self):
        tools.get("https:https://gitlab.com/graphviz/graphviz/-/archive/stable_release_{0}/graphviz-stable_release_{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("graphviz-stable_release_" + self.version):
            self.run("./autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
