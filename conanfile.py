from conans import ConanFile, AutoToolsBuildEnvironment, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.40.1"
    except:
        return None

class GraphvizConan(ConanFile):
    name = "graphviz"
    version = get_version()
    license = "EPL"
    description = "Graph Visualization Tools"
    url = "https://gitlab.com/graphviz/graphviz"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/0.1@%s/stable" % self.user)
        self.build_requires("autotools/1.0.0@%s/stable" % self.user)
        self.build_requires("flex/2.6.4@%s/stable" % self.user)
        self.build_requires("bison/3.3@%s/stable" % self.user)

    def source(self):
        tools.get("https:https://gitlab.com/graphviz/graphviz/-/archive/stable_release_{0}/graphviz-stable_release_{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("graphviz-stable_release_" + self.version):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
