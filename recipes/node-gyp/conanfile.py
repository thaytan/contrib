from build import *


class NodeGypRecipe(Recipe):
    description = "Node.js native addon build tool"
    license = "MIT"
    requires = ("nodejs/[^13.0.1]",)

    def source(self):
        tools.download(f"https://registry.npmjs.org/node-gyp/-/node-gyp-{self.version}.tgz", f"{self.name}-{self.version}.tgz")
