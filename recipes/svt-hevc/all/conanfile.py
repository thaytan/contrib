from build import *


class SvtHevcRecipe(Recipe):
    description = "The Scalable Video Technology for HEVC Encoder"
    license = "BSD"
    build_requires = (
        "cmake/[^3.15.3]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        self.get(f"https://github.com/OpenVisualCloud/SVT-HEVC/archive/v{self.version}.tar.gz")
