from build import *


class GStreamerRtspServerRecipe(Recipe):
    description = "A framework for streaming media"
    license = "LGPL"
    options = {
        "examples": [True, False],
        "tests": [True, False],
        "rtspclientsink": [True, False],
    }
    default_options = (
        "examples=False",
        "tests=False",
        "rtspclientsink=True",
    )
    build_requires = (
        "meson/[^0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "glib/[^2.62.0]",
        "gstreamer/[~1.16]",
        "gstreamer-plugins-base/[~1.16]",
    )

    def source(self):
        self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/archive/{self.version}/gst-rtsp-server-{self.version}.tar.gz")

    def build(self):
        args = []
        args.append("-Dcheck=" + ("enabled" if self.options.examples else "disabled"))
        args.append("-Dtools=" + ("enabled" if self.options.tests else "disabled"))
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Drtspclientsink=" + ("enabled" if self.options.rtspclientsink else "disabled"))
        self.meson(args)

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
