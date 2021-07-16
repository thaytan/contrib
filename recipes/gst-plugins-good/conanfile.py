from build import *


class GstPluginsGoodRecipe(GstRecipe):
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "LGPL"
    settings = GstRecipe.settings + ("hardware", )
    exports = "*.patch"
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
        "meson/[>=0.55.3]",
        "git/[^2.30.0]",
    )
    requires = ("gst-plugins-base/[^1.18]", )

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
        if "1.18" in self.settings.gstreamer:
            git = tools.Git(folder=f"{self.name}-{self.version}.src")
            git.clone(
                "https://gitlab.freedesktop.org/GStreamer/gst-plugins-good.git",
                self.version)
            if self.options.aivero_rvl_matroska:
                git.run(
                    '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../0001-matroska-add-support-for-custom-video-rvl-depth-map-.patch'
                )

            self.patch('gst-tags-in-mkv.patch')

            # Apply: vpxenc: add configure_encoder virtual method
            # Not required from 1.20 onward
            # https://gitlab.freedesktop.org/meh/gst-plugins-good/-/commit/c58436d97bb74d45338d237376312778b20751e8
            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../c58436d97bb74d45338d237376312778b20751e8.patch'
            )

            # Apply: vp9enc: expose tile-columns and tile-rows properties
            # Not required from 1.20 onward
            # https://gitlab.freedesktop.org/meh/gst-plugins-good/-/commit/75259ea6c0ad70cf7ff569bf3856255fadfaed2b
            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../75259ea6c0ad70cf7ff569bf3856255fadfaed2b.patch'
            )

            # Apply: vpxenc: change default for deadline to good quality
            # Not required from 1.20 onward
            # https://gitlab.freedesktop.org/meh/gst-plugins-good/-/commit/d3b70c1aab80fbaa4967121b04a179f1d7f9222f
            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../d3b70c1aab80fbaa4967121b04a179f1d7f9222f.patch'
            )

            # Apply: vp9enc: expose row-mt property
            # Not required from 1.20 onward
            # https://gitlab.freedesktop.org/meh/gst-plugins-good/-/commit/db6b580a23b72813caf4bfdc87f660bb36fbad3a
            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../db6b580a23b72813caf4bfdc87f660bb36fbad3a.patch'
            )

        else:
            self.get(
                f"https://github.com/GStreamer/gst-plugins-good/archive/{self.version}.tar.gz"
            )

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
