import os

from conans import *


class GStreamerVaapiConan(ConanFile):
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
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
        "base/[^1.0.0]",
        "meson/[^0.51.2]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "gstreamer-plugins-base/[~1.16]",
        "gstreamer-plugins-bad/[~1.16]",
        "libva/[^2.3.0]",
    )

    def source(self):
        git = tools.Git(folder=f"{self.name}-${self.version}")
        git.clone(url="https://gitlab.freedesktop.org/gstreamer/gstreamer-vaapi.git", branch=self.version, shallow=True)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dwith_encoders=" + ("yes" if self.options.encoders else "no"))
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name}-${self.version}", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
