from build import *


class GstK4a(GstRustProject):
    description = "GStreamer plugin containing `video/rgbd` source for an Azure Kinect DK (K4A) device"
    license = "LGPL"
    build_requires = ("rust/[^1.0.0]",)
    requires = (
        "k4a/[^1.4.1]",
        "capnproto/[^0.8.0]",
        f"gst-depth-meta/{branch()}",
        "rust-libstd/[^1.0.0]",
    )