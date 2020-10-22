import os
from conans import *


class NodeGypConan(ConanFile):
    description = "Node.js native addon build tool"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    )
    requires = (
        "base/[^1.0.0]",
        "nodejs/[^13.0.1]",
    )

    def source(self):
        tools.download(f"https://registry.npmjs.org/node-gyp/-/node-gyp-{self.version}.tgz", f"{self.name}-{self.version}.tgz")

    def build(self):
        self.run(f'npm install -g --user root --prefix "{self.package_folder}" "{self.name}-{self.version}.tgz"')
