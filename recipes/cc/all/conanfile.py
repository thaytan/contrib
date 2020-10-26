from build import *


class CCRecipe(Recipe):
    description = "Virtual c/c++ compiler package"
    license = "MIT"

    def requirements(self):
        self.requires(f"llvm/[^{self.settings.clang.version}]")
