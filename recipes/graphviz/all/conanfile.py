from conans import *


class GraphvizConan(ConanFile):
    description = "Graph Visualization Tools"
    license = "EPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "flex/[^2.6.4]",
        "bison/[^3.3]",
    )

    def source(self):
        tools.get(f"https://www2.graphviz.org/Packages/stable/portable_source/graphviz-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()
