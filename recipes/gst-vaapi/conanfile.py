from build import *


class GstVaapiRecipe(GstRecipe):
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "LGPL"
    options = {
        "encoders": [True, False],
    }
    default_options = (
        "encoders=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.55.3]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "libva/[^2.9.0]",
        "gst-plugins-bad/[^1.18]",
    )

    def source(self):
        self.get(f"https://github.com/GStreamer/gstreamer-vaapi/archive/{self.version}.tar.gz")

    def build(self):
        opts = {}
        opts["with_encoders"] = self.options.encoders
        self.meson(opts)
