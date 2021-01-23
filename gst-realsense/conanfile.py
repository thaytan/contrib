from build import *

class GstRealsense(GstRustProject):
    description = "GStreamer plugin containing `video/rgbd` source for a RealSense device"
    license = "LGPL"
    build_requires = (
        "rust/[^1.0.0]",
    )
    requires = (
        "librealsense/[^2.39.0]",
        "rgbd-timestamps/master",
    )
