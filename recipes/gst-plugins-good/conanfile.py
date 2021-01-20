from build import *


class GstPluginsGoodRecipe(GstRecipe):
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]", 
        "meson/[^0.55.3]",
    )
    requires = (
        "libvpx/[^1.8.0]",
        "libjpeg-turbo/[^2.0.3]",
        "gst-plugins-base/[^1.18]",
    )

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-plugins-good/archive/{self.version}.tar.gz")

    def build(self):
        opts = {
            "autodetect": True,
            "rtp": True,
            "rtsp": True,
            "rtpmanager": True,
            "udp": True,
            "png": True,
            "isomp4": True,
            "videofilter": True,
            "vpx": True,
            "multifile": True,
            "matroska": True,
            "videomixer": True,
            "ximagesrc": True,
            "ximagesrc-xdamage": True,
            "jpeg": True,
        }
        self.meson(opts)
