from build import *

class LibrealsenseSys(GstRustProject):
    description = "Rust FFI bindings for librealsense"
    license = "LGPL"
    build_requires = (
        "rust/[^1.0.0]",
    )
    requires = (
        f"gst-depth-meta/{branch()}",
        "librealsense/[^2.39.0]",
    )