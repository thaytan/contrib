from build import *


class GstUtil(GstRustProject):
    description = "Utility library for making it a bit easier to work with gstreamer from rust"
    license = "LGPL"
    build_requires = ("rust/[^1.0.0]")
    requires = ()
