from build import *


class GstPluginsBadRecipe(GstRecipe):
    description = "A set of plugins that aren't up to par compared to the rest"
    license = "LGPL"
    options = {
        "introspection": [True, False],
        "videoparsers": [True, False],
        "gl": [True, False],
        "nvcodec": [True, False],
        "pnm": [True, False],
        "webrtc": [True, False],
        "srtp": [True, False],
        "rtmp2": [True, False],
        "dtls": [True, False],
        "mpegtsmux": [True, False],
        "mpegtsdemux": [True, False],
        "debugutils": [True, False],
        "opencv": [True, False],
        "closedcaption": [True, False],
        "aiveropatchlatency": [True, False],
        "inter": [True, False],
        "webp": [True, False],
    }
    default_options = (
        "introspection=True",
        "videoparsers=True",
        "gl=True",
        "nvcodec=False",
        "pnm=True",
        "webrtc=True",
        "srtp=True",
        "rtmp2=True",
        "dtls=True",
        "mpegtsmux=True",
        "mpegtsdemux=True",
        "debugutils=True",
        "opencv=False",
        "closedcaption=False",
        "aiveropatchlatency=False",
        "inter=False",
        "webp=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "libnice/[^0.1.18]",
    )
    exports = "reduce_latency.patch"

    def configure(self):
        if self.settings.arch != "x86_64":
            self.options.remove("nvcodec")

    def build_requirements(self):
        if self.settings.arch == "x86_64" and self.options.nvcodec:
            self.build_requires("cuda/[~10.1]")
            self.build_requires("orc/[^0.4.31]")

    def requirements(self):
        if self.options.srtp:
            self.requires("libsrtp/[^2.2.0]")
        if self.options.opencv:
            self.requires("opencv/[^3.4.8]")
        if self.options.closedcaption:
            self.requires("pango/[^1.4.3]")
        if self.options.webp:
            self.requires("libwebp/[^1.1.0]")

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-plugins-bad/archive/{self.version}.tar.gz")

    def build(self):
        opts = {
            "videoparsers": self.options.videoparsers,
            "gl": self.options.gl,
            "pnm": self.options.pnm,
            "webrtc": self.options.webrtc,
            "srtp": self.options.srtp,
            "rtmp2": self.options.rtmp2,
            "dtls": self.options.srtp,
            "mpegtsmux": self.options.mpegtsmux,
            "mpegtsdemux": self.options.mpegtsdemux,
            "debugutils": self.options.debugutils,
            "opencv": self.options.opencv,
            "closedcaption": self.options.closedcaption,
            "inter": self.options.inter,
            "webp": self.options.webp,
        }
        if self.settings.arch == "x86_64":
            opts["nvcodec"] = self.options.nvcodec
        self.meson(opts)
