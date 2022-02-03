from build import *

class RgbdEnums(GstRustProject):
    description = "Definition of RGB-D enums for custom source elements that use video/rgbd CAPS"
    license = "LGPL"
    build_requires = (
        "rust/[^1.0.0]",
    )
    requires = (
        "glib/[^2.70.3]",
    )