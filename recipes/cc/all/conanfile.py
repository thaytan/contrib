from build import *


class CCRecipe(Recipe):
    description = "Virtual c/c++ compiler package"
    license = "MIT"

    def requirements(self):
        self.requires("libc/[^1.0.0]")
        self.requires(f"llvm/[^{self.settings.compiler.version}]")
