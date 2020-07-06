import os

from conans import *


class NodeGypConan(ConanFile):
    name = "node-gyp"
    description = "Node.js native addon build tool"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    )
    requires = (
        "base/[^1.0.0]",
        "nodejs/[^13.0.1]",
    )

    def source(self):
        tools.download(f"https://registry.npmjs.org/node-gyp/-/node-gyp-{self.version}.tgz", f"{self.name}-{self.version}.tgz")

    def build(self):
        self.run(f'npm install -g --user root --prefix "{self.package_folder}" "{self.name}-{self.version}.tgz"')
