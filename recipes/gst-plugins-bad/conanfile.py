from build import *


class GstPluginsBadRecipe(GstRecipe):
    description = "A set of plugins that aren't up to par compared to the rest"
    license = "LGPL"
    exports = "*.patch"
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
        "nvcodec=True",
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
        "meson/[>=0.55.3]",
        "gobject-introspection/[^1.59.3]",
        "gst-plugins-base/[^1.18]",
    )
    requires = ("libnice/[^0.1.18]", )

    def configure(self):
        if self.settings.arch != "x86_64":
            self.options.remove("nvcodec")
            self.options.remove("msdk")

    def build_requirements(self):
        if self.settings.arch == "x86_64" and self.options.nvcodec:
            self.build_requires("cuda/[>=11.2]")
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
            self.get(
                f"https://github.com/GStreamer/gst-plugins-bad/archive/{self.version}.tar.gz"
            )

        elif "1.18" in self.settings.gstreamer:
            git = tools.Git(folder=self.src)
            git.clone(
                "https://gitlab.freedesktop.org/GStreamer/gst-plugins-bad.git",
                "master")

            # Pick a random cutoff date close to HEAD on origin/master and try to build
            git.run("checkout 316ddddc160de4f1e5546ef1d70d21bce5459fea")

            # Build it for 1.18 by undoing some 1.19 specifics:
            # 9b082e7 undoes the requirement on gst 1.19
            # 6adf7df Fails to build - webp: allow per feature registration
            # 4f16edf Fails to build - srtp: allow per feature registration
            # a216a1f Fails to build - dtls: allow per feature registration
            # 42a8702 Fails to build - x265: allow per feature registration
            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" '
                + 'revert --no-edit ' +
                '9b082e7467797a6e1c5626a67f7ffc5d0248eccd ' +
                '4f16edf0d07e5fd42221d5e3727c6d5aa548cdb7 ' +
                '6adf7dff71b2808e8b5fbef7bf45f1ae50ae1b34 ' +
                'a216a1f2cf84b66601524be347ac4b45a995b044 ' +
                '42a87029190d8b13c8e2040e8b73147765bfd7a1 ')

            self.patch('74e04bc8d7f95f4636ac617f26e1b205040f9915.patch')

        elif "1.20" in self.settings.gstreamer:
            self.get(
                f"https://github.com/GStreamer/gst-plugins-bad/archive/{self.version}.tar.gz"
            )

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
