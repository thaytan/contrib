from build import *


class YarnRecipe(Recipe):
    description = "Fast, reliable, and secure dependency management"
    license = "BSD"
    build_requires = ("npm/[^7.0.5]",)
    requires = ("nodejs/[^15.1.0]",)

    def source(self):
        self.get(f"https://github.com/yarnpkg/yarn/releases/download/v{self.version}/yarn-v{self.version}.tar.gz")
