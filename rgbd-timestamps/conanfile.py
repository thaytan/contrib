from build import *


class RgbdTimestamps(GstRustProject):
    description = "Definition of RGB-D enums for custom source elements that use video/rgbd CAPS"
    license = "LGPL"
    build_requires = ("rust/[^1.0.0]",)
    requires = (
        "capnproto/[^0.8.0]",
        f"gst-depth-meta/{branch()}",
        "rust-libstd/[^1.0.0]",
    )