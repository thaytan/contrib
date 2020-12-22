from build import *


class GstPythonRecipe(Recipe):
    description = "Gstreamer Python bindings"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    requires = (
        "gstreamer/[~1.16]",
        "gobject-introspection/1.66.1",
        "python-gobject/3.33.1",
    )

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-python/archive/{self.version}.tar.gz")
