import os

from conans import *


class GStreamerLibavConan(ConanFile):
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
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
