from build import *


class LibxkbcommonRecipe(Recipe):
    description = "Keymap handling library for toolkits and window systems"
    license = "MIT"
    build_requires = (
        "meson/[^0.55.3]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
    )
    requires = (
        "libxcb/[^1.13.1]",
        "libxml2/[^2.9.10]",
    )

    def source(self):
        self.get(f"https://github.com/xkbcommon/libxkbcommon/archive/xkbcommon-{self.version}.tar.gz")

    def build(self):
        args = [
            "-Denable-wayland=false",
            "-Denable-docs=false",
        ]
        self.meson(args)
