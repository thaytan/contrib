from build import *


class GstK4a(GstRustProject):
    description = "GStreamer plugin containing `video/rgbd` source for an Azure Kinect DK (K4A) device"
    license = "LGPL"
    build_requires = ("rust/[^1.0.0]",)
    requires = (
        "libk4a/[^1.4.1]",
        "capnproto/[^0.8.0]",
        f"gst-depth-meta/{branch()}",
        "rust-libstd/[^1.0.0]",
    )

    def build(self):
        # We need to rebuild the rust bindings every time we tag a new release.
        self.cargo(clean=["libk4a", "libk4a-sys"])