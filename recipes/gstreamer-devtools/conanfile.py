from build import *


class GstDevtoolsRecipe(Recipe):
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    options = {
        "gtk_doc": [True, False],
        "introspection": [True, False],
        "tests": [True, False],
        "nls": [True, False],
    }
    default_options = (
        "gtk_doc=False",
        "introspection=False",
        "tests=True",
        "nls=False",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.51.2]",
    )
    requires = (
        "gst-plugins-base/[^1.16]",
        "json-glib/[~1.4.4]",
    )

    def source(self):
        git = tools.Git(folder="gst-devtools")
        git.clone("https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror.git", "rebased-aivero_mse_compare_changes")

    def build(self):
        self.meson(folder="gst-devtools")
