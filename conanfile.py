from build import *

class Rgbd(GstRustProject):
    description = "GStreamer plugin for demuxing and muxing `video/rgbd` streams"
    license = "LGPL"
    build_requires = (
        "rust/[^1.0.0]",
    )
    requires = (
        "gst-depth-meta/master",
        "capnproto/[^0.8.0]",
    )