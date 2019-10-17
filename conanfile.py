from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GraphvizConan(ConanFile):
    name = "graphviz"
    version = tools.get_env("GIT_TAG", "2.42.1")
    license = "EPL"
    description = "Graph Visualization Tools"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("flex/[>=2.6.4]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://www2.graphviz.org/Packages/stable/portable_source/graphviz-%s.tar.gz"
            % self.version
        )

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()
