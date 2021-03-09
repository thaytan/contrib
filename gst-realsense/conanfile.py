from build import *


class GstRealsense(GstRustProject):
    description = "GStreamer plugin containing `video/rgbd` source for a RealSense device"
    license = "LGPL"
    build_requires = ("rust/[^1.0.0]",)
    requires = (
        "librealsense/[^2.39.0]",
        f"rgbd-timestamps/{branch()}",
    )

    def build(self):
        # We need to rebuild the rust bindings every time we tag a new release.
        self.cargo(clean=["librealsense2", "librealsense2-sys"])