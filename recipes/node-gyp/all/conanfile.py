import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class NodeGypConan(ConanFile):
    name = "node-gyp"
    description = "Node.js native addon build tool"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires("generators/1.0.0@%s/stable" % self.user)
        self.requires("nodejs/[>=13.0.1]@%s/stable" % self.user)

    def source(self):
        tools.download(
            f"https://registry.npmjs.org/node-gyp/-/node-gyp-{self.version}.tgz",
            f"{self.name}-{self.version}.tgz",
        )

    def build(self):
        self.run(
            f'npm install -g --user root --prefix "{self.package_folder}" "{self.name}-{self.version}.tgz"'
        )
