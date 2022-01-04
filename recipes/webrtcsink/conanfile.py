from build import *
from conans.errors import ConanInvalidConfiguration


class GstRecipe(GstRecipe):
    description = "All-batteries included GStreamer WebRTC producer"
    license = "MIT"
    build_requires = ("rust/[^1.0.0]",)
    requires = ("rust-libstd/[^1.0.0]",)

    def requirements(self):
        self.requires(f"gst/[~{self.settings.gstreamer}]")

    def source(self):
        self.get(f"https://github.com/centricular/webrtcsink/archive/{self.version}.tar.gz")
