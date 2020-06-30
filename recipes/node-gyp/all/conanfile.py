import os

from conans import *


class NodeGypConan(ConanFile):
    description = "Node.js native addon build tool"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def requirements(self):
        self.requires("generators/1.0.0")
        self.requires("nodejs/[^13.0.1]")

    def source(self):
        tools.download(f"https://registry.npmjs.org/node-gyp/-/node-gyp-{self.version}.tgz", f"{self.name}-{self.version}.tgz")

    def build(self):
        self.run(f'npm install -g --user root --prefix "{self.package_folder}" "{self.name}-{self.version}.tgz"')
