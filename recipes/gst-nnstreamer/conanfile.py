from build import *


class GstNnstreamer(GstRecipe):
    description = "Neural Network (NN) Streamer, Stream Processing Paradigm for Neural Network Apps/Devices."
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.57.2]",
        "git/[^2.30.0]",
        "flex/[^2.6.4]",
        "bison/[^3.7.2]",
    )

    def requirements(self):
        self.requires(f"gst-plugins-base/[~{self.settings.gstreamer}]")

    def source(self):
        self.get(f"https://github.com/nnstreamer/nnstreamer/archive/refs/tags/v{self.version}.tar.gz")

    def build(self):
        opts = {
            "werror": False,
        }
        self.meson(opts)
