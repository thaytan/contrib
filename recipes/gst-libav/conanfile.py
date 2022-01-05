from build import *


class GstLibavRecipe(GstRecipe):
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.55.3]",
    )
    requires = ("ffmpeg/[^4.1]",)

    def requirements(self):
        self.requires(f"gst-plugins-base/[~{self.settings.gstreamer}]")

    def source(self):
        version = self.version
        if version == "1.20.0":
            version = "428a9a6c012bde4ddd93d37818558351013afe65"

        self.get(f"https://gitlab.freedesktop.org/gstreamer/gstreamer/-/archive/{version}.tar.gz")

    def build(self):
        source_folder = os.path.join(self.src, "subprojects", "gst-libav")
        self.meson({}, source_folder)
