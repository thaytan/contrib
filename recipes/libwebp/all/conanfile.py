from build import *


class RecipeLibwebp(Recipe):
    description = "library to encode and decode images in WebP format"
    license = "BSD"
    build_requires = ("cc/[^1.0.0]", "cmake/[^3.18.4]")

    def source(self):
        self.get(f"https://github.com/webmproject/libwebp/archive/v{self.version}.tar.gz")

    def build(self):
        defs = {
            "BUILD_SHARED_LIBS": self.options.shared,
        }
        self.cmake(defs)
