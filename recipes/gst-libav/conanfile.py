from build import *


class GstLibavRecipe(Recipe):
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "GPL"
    build_requires = ("cc/[^1.0.0]", "meson/[^0.51.2]")
    requires = (
        "glib/[^2.58.1]",
        "gst-plugins-base/[^1.18.1]",
        "ffmpeg/[^4.1]",
    )

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-libav/archive/{self.version}.tar.gz")
