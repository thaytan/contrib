from build import *


class XcbProtoRecipe(Recipe):
    description = "XML-XCB protocol descriptions"
    license = "MIT"
    build_requires = ("autotools/[^1.0.0]",)

    def source(self):
        self.get(f"https://xcb.freedesktop.org/dist/xcb-proto-{self.version}.tar.xz")
