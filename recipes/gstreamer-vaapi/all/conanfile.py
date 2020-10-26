import os

from conans import *


class GStreamerVaapiConan(ConanFile):
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
        "meson/[^0.55.3]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = ("libva/[^2.9.0]",)

    def requirements(self):
        self.requires(f"gstreamer-plugins-bad/[~{self.settings.gstreamer}]")

    def source(self):
        tools.get(f"https://github.com/GStreamer/gstreamer-vaapi/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dwith_encoders=" + ("yes" if self.options.encoders else "no"))
        meson = Meson(self)
        meson.configure(args, source_folder=f"gstreamer-vaapi-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
