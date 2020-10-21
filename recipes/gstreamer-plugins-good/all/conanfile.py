import os

from conans import *


class GStreamerPluginsGoodConan(ConanFile):
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {
        "autodetect": [True, False],
        "rtp": [True, False],
        "rtsp": [True, False],
        "udp": [True, False],
        "png": [True, False],
        "isomp4": [True, False],
        "videofilter": [True, False],
        "vpx": [True, False],
        "multifile": [True, False],
        "matroska": [True, False],
        "videomixer": [True, False],
        "ximagesrc": [True, False],
        "ximagesrc_xdamage": [True, False],
        "ximagesrc_xshm": [True, False],
        "jpeg": [True, False],
    }
    default_options = (
        "autodetect=True",
        "rtp=True",
        "rtsp=True",
        "udp=True",
        "png=True",
        "isomp4=True",
        "videofilter=True",
        "vpx=True",
        "multifile=True",
        "matroska=True",
        "videomixer=True",
        "ximagesrc=True",
        "ximagesrc_xdamage=False",
        "ximagesrc_xshm=True",
        "jpeg=True",
    )
    build_requires = (
        "base/[^1.0.0]",
        "meson/[^0.51.2]",
    )
    requires = (
        "glib/[^2.62.0]",
        "gstreamer-plugins-base/[~1.16]",
        "libpng/[^1.6.37]",
        "libvpx/[^1.8.0]",
        "libjpeg-turbo/[^2.0.3]",
    )

    def source(self):
        git = tools.Git(folder="gst-plugins-good-" + self.version)
        # This needs to stay in place until we have ditched the 1.16 Gstreamer version.
        git.clone("https://gitlab.freedesktop.org/thaytan/gst-plugins-good", "splitmuxsink-muxerpad-map-1.16.0")

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dautodetect=" + ("enabled" if self.options.autodetect else "disabled"))
        args.append("-Drtp=" + ("enabled" if self.options.rtp else "disabled"))
        args.append("-Drtsp=" + ("enabled" if self.options.rtsp else "disabled"))
        args.append("-Drtpmanager=" + ("enabled" if self.options.rtp else "disabled"))
        args.append("-Dudp=" + ("enabled" if self.options.udp else "disabled"))
        args.append("-Dpng=" + ("enabled" if self.options.png else "disabled"))
        args.append("-Disomp4=" + ("enabled" if self.options.isomp4 else "disabled"))
        args.append("-Dvideofilter=" + ("enabled" if self.options.videofilter else "disabled"))
        args.append("-Dvpx=" + ("enabled" if self.options.vpx else "disabled"))
        args.append("-Dmultifile=" + ("enabled" if self.options.multifile else "disabled"))
        args.append("-Dmatroska=" + ("enabled" if self.options.matroska else "disabled"))
        args.append("-Dvideomixer=" + ("enabled" if self.options.videomixer else "disabled"))
        args.append("-Dximagesrc=" + ("enabled" if self.options.ximagesrc else "disabled"))
        args.append("-Dximagesrc-xdamage=" + ("enabled" if self.options.ximagesrc_xdamage else "disabled"))
        args.append("-Dxshm=" + ("enabled" if self.options.ximagesrc_xshm else "disabled"))
        args.append("-Djpeg=" + ("enabled" if self.options.jpeg else "disabled"))

        meson = Meson(self)
        meson.configure(source_folder=f"gst-plugins-good-{self.version}", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
