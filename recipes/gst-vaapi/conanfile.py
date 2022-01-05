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
        "intel-vaapi-driver/[^2.4.1]",
        "eudev/[^3.2.9]",
    )

    def requirements(self):
        self.requires(f"gst-plugins-bad/[~{self.settings.gstreamer}]")

    def source(self):
        version = self.version
        if version == "1.20.0":
            version = "428a9a6c012bde4ddd93d37818558351013afe65"

        self.get(f"https://gitlab.freedesktop.org/gstreamer/gstreamer/-/archive/{version}.tar.gz")

    def build(self):
        source_folder = os.path.join(self.src, "subprojects", "gstreamer-vaapi")
        opts = {
            "with_drm": self.options.drm,
            "with_egl": self.options.egl,
            "with_encoders": self.options.encoders,
            "with_glx": self.options.glx,
            "with_x11": self.options.x11,
            "with_wayland": self.options.wayland,
            "tests": self.options.tests,
        }
        self.meson(opts, source_folder)

    def package(self):
        super().package()
        self.copy("*.adoc")
        self.copy("*.sh", dst="scripts")
