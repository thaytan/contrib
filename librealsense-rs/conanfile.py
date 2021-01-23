from build import *

class Librealsense(GstRustProject):
    description = "Rust FFI bindings for librealsense"
    license = "LGPL"
    build_requires = (
        "rust/[^1.0.0]",
    )
    requires = (
        "gst-depth-meta/master",
        "librealsense/[^2.39.0]",
    )