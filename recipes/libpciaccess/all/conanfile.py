from build import *


class LibPciAccessRecipe(Recipe):
    description = "Generic PCI access library"
    license = "MIT"
    build_requires = (
        "make/[^4.3]",
        "xorg-util-macros/[^1.19.1]",
    )

    def source(self):
        self.get(f"https://xorg.freedesktop.org/releases/individual/lib/libpciaccess-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        self.autotools(args)
