import os

from conans import *


class GStreamerPythonConan(ConanFile):
    description = "Gstreamer Python bindings"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
        requires = (
        "gstreamer/[~1.16]",
        "gobject-introspection/1.59.3",
        "python-gobject/3.33.1",
    )

    def source(self):
        tools.get(f"https://github.com/GStreamer/gst-python/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-python-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()