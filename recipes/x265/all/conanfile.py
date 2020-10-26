from build import *


class X265Recipe(Recipe):
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "GPL"
    options = {"high_bit_depth": [True, False], "main12": [True, False], "hdr10": [True, False]}
    default_options = "bit_depth=False", "main12=True", "hdr10=False"
    build_requires = (
        "cmake/[^3.18.4]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        self.get(f"https://github.com/videolan/x265/archive/{self.version}.tar.gz")

    def build(self):
        defs = {
            "HIGH_BIT_DEPTH": self.options.high_bit_depth,
            "MAIN12": self.options.main12,
            "ENABLE_HDR10_PLUS": self.options.hdr10,
        }
        self.cmake(defs)
