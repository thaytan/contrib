from build import *


class GstSvtHevcRecipe(GstRecipe):
    description = "The Scalable Video Technology for HEVC Encoder GStreamer plugin"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.51.2]",
    )
    requires = (
        "svt-hevc/[^1.4.3]",
    )

    def requirements(self):
        self.requires(f"gst-plugins-base/[~{self.settings.gstreamer}]")
    def source(self):
        self.get(f"https://github.com/OpenVisualCloud/SVT-HEVC/archive/v{self.version}.tar.gz")
