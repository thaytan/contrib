from build import *


class LibepoxyRecipe(Recipe):
    description = "Library handling OpenGL function pointer management"
    license = "MIT"
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True",)
    build_requires = ("cc/[^1.0.0]", "meson/[^0.55.3]")
    requires = ("mesa/[^20.2.1]",)

    def requirements(self):
        if self.options.x11:
            self.requires("libx11/[^1.6.8]")

    def source(self):
        self.get(f"https://github.com/anholt/libepoxy/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "-Dglx=yes",
            "-Dtests=false",
            f"-Dx11={self.options.x11}",
        ]
        self.meson(args)
