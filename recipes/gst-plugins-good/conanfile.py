from build import *


class GstPluginsGoodRecipe(GstRecipe):
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "LGPL"
    settings = GstRecipe.settings + ("hardware",)
    exports = "0001-matroska-add-support-for-custom-video-rvl-depth-map-.patch"
    options = {
        "aivero_rvl_matroska": [True, False],
        "autodetect": [True, False],
        "isomp4": [True, False],
        "jpeg": [True, False],
        "matroska": [True, False],
        "multifile": [True, False],
        "png": [True, False],
        "rtp": [True, False],
        "rtsp": [True, False],
        "udp": [True, False],
        "videofilter": [True, False],
        "videomixer": [True, False],
        "vpx": [True, False],
        "ximagesrc_xdamage": [True, False],
        "ximagesrc_xshm": [True, False],
        "ximagesrc": [True, False],
        "v4l2": [True, False],
    }
    default_options = (
        "aivero_rvl_matroska=True",
        "autodetect=True",
        "isomp4=True",
        "jpeg=True",
        "matroska=True",
        "multifile=True",
        "png=True",
        "rtp=True",
        "rtsp=True",
        "udp=True",
        "videofilter=True",
        "videomixer=True",
        "vpx=True",
        "ximagesrc_xdamage=False",
        "ximagesrc_xshm=True",
        "ximagesrc=True",
        "v4l2=False",
    )

    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "git/[^2.30.0]",
    )
    requires = ("gst-plugins-base/[^1.18]",)

    def configure(self):
        if self.settings.hardware == "rpi":
            if self.settings.arch == "armv8":
                # enable v4l2 for rpi 64-bit
                self.options.v4l2 = True

    def requirements(self):
        # gst-plugins-bad -> pango -> freetype -> png
        # if self.options.png:
        #     self.requires("libpng/[^1.6.37]")
        if self.options.vpx:
            self.requires("libvpx/[^1.8.0]")
        if self.options.jpeg:
            self.requires("libjpeg-turbo/[^2.0.3]")

    def source(self):
        # This needs to stay in place until we have ditched the 1.16 Gstreamer version.
        if "1.18" in self.settings.gstreamer:
            git = tools.Git(folder=f"{self.name}-{self.version}.src")
            git.clone("https://gitlab.freedesktop.org/meh/gst-plugins-good.git", "1.18-backports")
            if self.options.aivero_rvl_matroska:
                git.run('-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../0001-matroska-add-support-for-custom-video-rvl-depth-map-.patch')
        else:
            self.get(f"https://github.com/GStreamer/gst-plugins-good/archive/{self.version}.tar.gz")

    def build(self):
        opts = {
            "autodetect": True,
            "isomp4": True,
            "jpeg": True,
            "matroska": True,
            "multifile": True,
            "png": True,
            "rtp": True,
            "rtpmanager": True,
            "rtsp": True,
            "udp": True,
            "videofilter": True,
            "videomixer": True,
            "vpx": True,
            "ximagesrc-xdamage": True,
            "ximagesrc": True,
        }
        opts["v4l2"] = self.options.v4l2
        self.meson(opts)
