from build import *


class GstVaapiRecipe(Recipe):
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    options = {
        "encoders": [True, False],
        "egl": [True, False],
        "x11": [True, False],
        "drm": [True, False],
        "glx": [True, False],
    }
    default_options = (
        "encoders=True",
        "egl=True",
        "x11=True",
        "drm=True",
        "glx=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "libva/[^2.9.0]",
        "gst-plugins-bad/[^1.18]",
    )

    def source(self):
        self.get(f"https://github.com/GStreamer/gstreamer-vaapi/archive/{self.version}.tar.gz")

    def build(self):
        args = []
        args.append("-Dwith_encoders=" + ("yes" if self.options.encoders else "no"))
        self.meson(args)
