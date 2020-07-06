import os

from conans import *


class GStreamerLibavConan(ConanFile):
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("meson/[^0.51.2]",)
    requires = (
        "glib/[^2.58.1]",
        "gstreamer-plugins-base/[~1.16]",
        "ffmpeg/[^4.1]",
    )

    def source(self):
        tools.get(f"https://github.com/GStreamer/gst-libav/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-libav-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
