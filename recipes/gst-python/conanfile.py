from build import *


class GstPythonRecipe(GstRecipe):
    description = "Gstreamer Python bindings"
    license = "LGPL"
    requires = (
        "gobject-introspection/^1.66.1",
        "python-gobject/^3.33.1",
    )
    def requirements(self):
        self.requires(f"gstreamer/[~{self.settings.gstreamer}]")
    def source(self):
        self.get(f"https://github.com/GStreamer/gst-python/archive/{self.version}.tar.gz")
