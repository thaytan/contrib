from build import *


class GstPythonRecipe(GstRecipe):
    description = "Gstreamer Python bindings"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.55.3]",
    )
    requires = ("python-gobject/[^3.33.1]",)

    def requirements(self):
        self.requires(f"gst/[~{self.settings.gstreamer}]")

    def source(self):
        version = self.version
        if version == "1.20.0":
            version = "428a9a6c012bde4ddd93d37818558351013afe65"

        self.get(f"https://gitlab.freedesktop.org/gstreamer/gstreamer/-/archive/{version}.tar.gz")

    def build(self):
        source_folder = os.path.join(self.src, "subprojects", "gst-python")
        self.meson({}, source_folder)
