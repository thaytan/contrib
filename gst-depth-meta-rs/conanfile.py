from build import *

class GstDepthMetaRs(GstRustProject):
    description = "Definition of RGB-D enums for custom source elements that use video/rgbd CAPS"
    license = "LGPL"
    build_requires = (
        "rust/[^1.0.0]",
        "capnproto/[^0.8.0]",
    )
    requires = (
        "gst-depth-meta/master",
    )