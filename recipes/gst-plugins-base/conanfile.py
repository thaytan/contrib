from build import *


class GstPluginsBaseRecipe(GstRecipe):
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "LGPL"
    options = {
        "shared": [True, False],
        "introspection": [True, False],
        "x11": [True, False],
        "audioresample": [True, False],
    }
    default_options = (
        "shared=True",
        "introspection=True",
        "x11=True",
        "audioresample=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.2]",
    )
    requires = (
        "gst/[^1.18]",
        "opus/[^1.3.1]",
        "pango/[^1.43.0]",
        "orc/[^0.4.29]",
        "mesa/[>=20.2.1]",
    )

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.66.1]")

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-plugins-base/archive/{self.version}.tar.gz")

    def build(self):
        opts = {
            "gl_platform": "egl",
            "introspection": self.options.introspection,
            "x11": self.options.x11,
            "audioresample": self.options.audioresample,
            "gl": True,
            "videotestsrc": True,
            "audiotestsrc": True,
            "videoconvert": True,
            "app": True,
            "playback": True,
            "typefind": True,
            "orc": True,
            "opus": True,
            "pango": True,
            "videoscale": True,
            "audioconvert": True,
        }
        self.meson(opts)
