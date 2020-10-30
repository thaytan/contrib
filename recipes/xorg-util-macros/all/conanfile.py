from build import *


class XorgUtilMacrosRecipe(Recipe):
    description = "X.Org Autotools macros"
    license = "custom"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )

    def source(self):
        self.get(f"https://xorg.freedesktop.org/releases/individual/util/util-macros-{self.version}.tar.gz")
