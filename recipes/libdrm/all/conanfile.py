from build import *


class LibdrmRecipe(Recipe):
    description = "Direct Rendering Manager headers and kernel modules"
    license = "MIT"
    build_requires = (
        "meson/[^0.55.3]",
        "libpciaccess/[>=0.16]",
    )

    def source(self):
        self.get(f"http://dri.freedesktop.org/libdrm/libdrm-{self.version}.tar.xz")

    def build(self):
        args = [
            "-Dradeon=false",
            "-Damdgpu=true",
            "-Dnouveau=true",
        ]
        self.meson(args)
