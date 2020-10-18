import os

from conans import *


class GStreamerSvtHevcConan(ConanFile):
    description = "The Scalable Video Technology for HEVC Encoder GStreamer plugin"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "base/[^1.0.0]",
        "meson/[^0.51.2]",
    )
    requires = (
        "gstreamer-plugins-base/[^1.16.2]",
        "svt-hevc/[^1.4.3]",
    )

    def source(self):
        tools.get(f"https://github.com/OpenVisualCloud/SVT-HEVC/archive/v{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder=f"SVT-HEVC-{self.version}/gstreamer-plugin")
        meson.install()
