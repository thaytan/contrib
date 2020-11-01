from build import *


class GperfRecipe(Recipe):
    description = "A portable, high level programming interface to various calling conventions"
    license = "GPL3"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
    )

    def source(self):
        self.get("https://gitlab.com/aivero/public/gperf/-/archive/meson/gperf-meson.tar.gz")
