from build import *


class GstRtspServerRecipe(GstRecipe):
    description = "A framework for streaming media"
    license = "LGPL"
    options = {
        "examples": [True, False],
        "tests": [True, False],
        "introspection": [True, False],
        "rtspclientsink": [True, False],
    }
    default_options = (
        "examples=False",
        "tests=False",
        "introspection=True",
        "rtspclientsink=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "gst-plugins-base/[^1.18]",
    )

    def source(self):
        self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/archive/{self.version}/gst-rtsp-server-{self.version}.tar.gz")

    def build(self):
        opts = {}
        opts["examples"] = self.options.examples
        opts["tests"] = self.options.tests
        opts["introspection"] = self.options.introspection
        opts["rtspclientsink"] = self.options.rtspclientsink
        self.meson(opts)