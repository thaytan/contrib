from build import *


class CCRecipe(Recipe):
    description = "Virtual c/c++ compiler package"
    license = "GPL"
    requires = ("llvm/[^11.0.0]",)
