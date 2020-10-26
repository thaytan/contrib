from build import *


class GStreamerRecipe(Recipe):
    description = "A framework for streaming media"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    build_requires = (
        "meson/[^0.55.3]",
        "bison/[^3.7.2]",
        "flex/[^2.6.4]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = ("glib/[^2.62.0]",)

    def source(self):
        self.get(f"https://github.com/GStreamer/gstreamer/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "-Dcheck=enabled",
            "-Dtools=enabled",
            "-Dintrospection=enabled",
        ]
        self.meson(args)

    def package_info(self):
        self.env_info.GST_PLUGIN_SCANNER = os.path.join(self.package_folder, "bin", "gstreamer-1.0", "gst-plugin-scanner")
