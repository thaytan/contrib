from build import *


class GStreamerSvtHevcRecipe(Recipe):
    description = "The Scalable Video Technology for HEVC Encoder GStreamer plugin"
    license = "LGPL"
    build_requires = (
        "base/[^1.0.0]",
        "meson/[^0.51.2]",
    )
    requires = (
        "gstreamer-plugins-base/[^1.16.2]",
        "svt-hevc/[^1.4.3]",
    )

    def source(self):
        self.get(f"https://github.com/OpenVisualCloud/SVT-HEVC/archive/v{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        self.meson(args)
