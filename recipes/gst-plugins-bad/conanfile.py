from build import *


class GstPluginsBadRecipe(GstRecipe):
    description = "A set of plugins that aren't up to par compared to the rest"
    license = "LGPL"
    options = {
        "closedcaption": [True, False],
        "debugutils": [True, False],
        "dtls": [True, False],
        "gl": [True, False],
        "inter": [True, False],
        "introspection": [True, False],
        "mpegtsdemux": [True, False],
        "mpegtsmux": [True, False],
        "msdk": [True, False],
        "nvcodec": [True, False],
        "opencv": [True, False],
        "pnm": [True, False],
        "rtmp2": [True, False],
        "srtp": [True, False],
        "videoparsers": [True, False],
        "webp": [True, False],
        "webrtc": [True, False],
        "x265": [True, False],
    }
    default_options = (
        "closedcaption=False",
        "debugutils=True",
        "dtls=True",
        "gl=True",
        "inter=False",
        "introspection=True",
        "mpegtsdemux=True",
        "mpegtsmux=True",
        "msdk=False",
        "nvcodec=False",
        "opencv=False",
        "pnm=True",
        "rtmp2=True",
        "srtp=True",
        "videoparsers=True",
        "webp=True",
        "webrtc=True",
        "x265=False",
    )

    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "gobject-introspection/[^1.59.3]",
        "gst-plugins-base/[^1.18]",
    )
    requires = ("libnice/[^0.1.18]",)

    def configure(self):
        if self.settings.arch != "x86_64":
            self.options.remove("nvdec")
            self.options.remove("nvenc")
            self.options.remove("nvcodec")
            self.options.remove("msdk")

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
        if self.settings.arch == "x86_64" and (self.options.msdk):
            self.requires("intel-media-sdk/[>=20.2]")
            self.requires("libgudev/[>=233]")
        if self.options.x265:
            self.requires("x265/[>=2.7]")

    def source(self):
        git = tools.Git(folder="gst-plugins-bad")
        if "1.16" in self.settings.gstreamer:
            print("Getting {self.settings.gstreamer} from https://gitlab.freedesktop.org/meh/gst-plugins-bad.git")
            self.get(f"https://github.com/GStreamer/gst-plugins-bad/archive/{self.version}.tar.gz")

        elif "1.18" in self.settings.gstreamer:
            self.get(f"https://gitlab.freedesktop.org/meh/gst-plugins-bad/-/archive/1.18-backports/gst-plugins-bad-1.18-backports.tar.gz")

    def build(self):
        opts = {
            "closedcaption": self.options.closedcaption,
            "debugutils": self.options.debugutils,
            "dtls": self.options.dtls,
            "gl": self.options.gl,
            "inter": self.options.inter,
            "mpegtsdemux": self.options.mpegtsdemux,
            "mpegtsmux": self.options.mpegtsmux,
            "opencv": self.options.opencv,
            "pnm": self.options.pnm,
            "rtmp2": self.options.rtmp2,
            "srtp": self.options.srtp,
            "videoparsers": self.options.videoparsers,
            "webp": self.options.webp,
            "webrtc": self.options.webrtc,
            "x265": self.options.x265,
        }
        if self.settings.arch == "x86_64":
            opts["msdk"] = self.options.msdk
            opts["nvcodec"] = self.options.nvcodec
        self.meson(opts)
