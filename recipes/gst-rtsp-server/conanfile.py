from build import *


class GstRtspServerRecipe(GstRecipe):
    description = "A framework for streaming media"
    license = "LGPL"
    options = {
        "examples": [True, False],
        "tests": [True, False],
        "rtspclientsink": [True, False],
    }
    default_options = (
        "examples=False",
        "tests=False",
        "rtspclientsink=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "glib/[^2.62.0]",
        "gstreamer/[~1.16]",
        "gstreamer-plugins-base/[~1.16]",
    )

    def source(self):
        self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/archive/{self.version}/gst-rtsp-server-{self.version}.tar.gz")

    def build(self):
        opts = {}
        opts["check"] = self.options.examples
        opts["tools"] = self.options.tests
        opts["introspection"] = self.options.introspection
        opts["rtspclientsink"] = self.options.rtspclientsink
        self.meson(opts)