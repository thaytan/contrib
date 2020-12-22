from build import *


class GStreamerRecipe(GstreamerRecipe):
    description = "A framework for streaming media"
    license = "LGPL"
    options = {
        "shared": [True, False],
        "introspection": [True, False],
    }
    default_options = (
        "shared=True",
        "introspection=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "bison/[^3.7.2]",
        "flex/[^2.6.4]",
    )
    requires = ("glib/[^2.66.1]",)

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.66.1]",)

    def source(self):
        self.get(f"https://github.com/GStreamer/gstreamer/archive/{self.version}.tar.gz")

    def build(self):
        opts = {
            "check": True,
            "tools": True,
            "introspection": self.options.introspection,
        }
        self.meson(opts)

    def package_info(self):
        self.env_info.GST_PLUGIN_SCANNER = os.path.join(self.package_folder, "bin", "gstreamer-1.0", "gst-plugin-scanner")
