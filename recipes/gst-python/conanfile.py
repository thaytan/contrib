from build import *


class GstPythonRecipe(GstRecipe):
    description = "Gstreamer Python bindings"
    license = "LGPL"
    requires = ("python-gobject/[^3.33.1]",)

    def requirements(self):
        self.requires(f"gst/[~{self.settings.gstreamer}]")

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-python/archive/{self.version}.tar.gz")
