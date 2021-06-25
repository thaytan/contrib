from build import *


class GstRealsense(GstRustProject):
    description = "GStreamer plugin containing `video/rgbd` source for a RealSense device"
    license = "LGPL"
    build_requires = ("rust/[^1.0.0]", "capnproto/[^0.8]")
    requires = (
        "capnproto/[^0.8.0]",
        "libk4a/[^1.4.1]",
        "librealsense/[^2.39.0]",
        "rust-libstd/[^1.0.0]",
        f"gst-depth-meta/{branch()}",
    )

    def build(self):
        # We need to rebuild the rust bindings every time we tag a new release.
        self.cargo(clean=[
            "librealsense2", "librealsense2-sys", "libk4a", "libk4a-sys"
        ])
