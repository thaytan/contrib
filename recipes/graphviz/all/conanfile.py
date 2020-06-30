from conans import *


class GraphvizConan(ConanFile):
    description = "Graph Visualization Tools"
    license = "EPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autotools/[^1.0.0]")
        self.build_requires("flex/[^2.6.4]")
        self.build_requires("bison/[^3.3]")

    def source(self):
        tools.get("https://www2.graphviz.org/Packages/stable/portable_source/graphviz-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()
