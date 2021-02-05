from build import *


class GstVaapiRecipe(GstRecipe):
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "LGPL"
    options = {
        "drm": [True, False],
        "egl": [True, False],
        "encoders": [True, False],
        "glx": [True, False],
        "x11": [True, False],
        "wayland": [True, False],
        "tests": [True, False],
    }
    default_options = (
        "drm=True",
        "egl=True",
        "encoders=True",
        "glx=True",
        "x11=True",
        "wayland=False",
        "tests=True",
    )
    exports = ["vaapi_env.sh", "README_gst-vaapi.adoc"]
    build_requires = (
        "cc/[^1.0.0]",
        "gobject-introspection/[^1.59.3]",
        "meson/[>=0.55.3]",
    )
    requires = (
        "gst-plugins-bad/[^1.18]",
        "intel-vaapi-driver/[^2.4.1]",
        "eudev/[^3.2.9]",
    )

    def source(self):
        self.get(f"https://github.com/GStreamer/gstreamer-vaapi/archive/{self.version}.tar.gz")

    def build(self):
        opts = {}
        opts["with_drm"] = self.options.drm
        opts["with_egl"] = self.options.egl
        opts["with_encoders"] = self.options.encoders
        opts["with_glx"] = self.options.glx
        opts["with_x11"] = self.options.x11
        opts["with_wayland"] = self.options.wayland
        opts["tests"] = self.options.tests
        self.meson(opts)

    def package(self):
        super().package()
        self.copy("*.adoc")
        self.copy("*.sh", dst="scripts")
