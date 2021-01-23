from build import *


class GstPythonRecipe(Recipe):
    description = "Gstreamer Python bindings"
    license = "LGPL"
    requires = (
        "gstreamer/[~1.16]",
        "gobject-introspection/1.66.1",
        "python-gobject/3.33.1",
    )

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-python/archive/{self.version}.tar.gz")
