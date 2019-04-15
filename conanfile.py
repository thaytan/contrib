import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.util import files


class GraphvizConan(ConanFile):
    version = "2.40.1"
    name = "graphviz"
    license = "https://gitlab.com/graphviz/graphviz/blob/master/LICENSE"
    description = "Graph Visualization Tools"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://gitlab.com/graphviz/graphviz"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"

    def requirements(self):
        self.requires("flex/2.6.4@%s/%s" % (self.user, self.channel), private=True)
        self.requires("bison/3.2.4@%s/%s" % (self.user, self.channel), private=True)

    def source(self):
        tools.get("https://gitlab.com/graphviz/graphviz/-/archive/stable_release_{0}/graphviz-stable_release_{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir(os.path.join(self.source_folder, "graphviz-stable_release_" + self.version)):
            self.run("./autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.make(args=["install"])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
