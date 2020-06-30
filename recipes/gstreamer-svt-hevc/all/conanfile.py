import os

from conans import *


class GStreamerSvtHevcConan(ConanFile):
    description = "The Scalable Video Technology for HEVC Encoder GStreamer plugin"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/[^1.0.0]",
        "meson/[^0.51.2]",
    )
    requires = (
        "gstreamer-plugins-base/[^1.16.2]",
        "svt-hevc/[^1.4.3]",
    )

    def source(self):
        tools.get("https://github.com/OpenVisualCloud/SVT-HEVC/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="SVT-HEVC-%s/gstreamer-plugin" % self.version)
        meson.install()
