from build import *


class YasmRecipe(Recipe):
    description = "Yasm is a complete rewrite of the NASM assembler under the new BSD License"
    license = "BSD"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        self.get(f"http://www.tortall.net/projects/yasm/releases/yasm-{self.version}.tar.gz")

    def build(self):
        self.autotools()
