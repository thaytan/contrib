from build import *


class GstDevtoolsRecipe(GstRecipe):
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
        "cc/[>=1.0.0]",
        "meson/[>=0.51.2]",
        "pkgconf/[^1.7.3]",
    )
    requires = (
        "gst-plugins-base/[>=1.18]",
        "json-glib/[>=1.6.2]",
    )

    def source(self):
        # if "1.18" in self.settings.gstreamer:
        #     self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-devtools/-/archive/{self.version}/gst-devtools-{self.version}.tar.bz2")
        # else:
        #     self.get(f"https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror/-/archive/{self.version}/gst-devtools-mirror-{self.version}.tar.gz")
        self.get(f"https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror/-/archive/{self.version}/gst-devtools-mirror-{self.version}.tar.gz")