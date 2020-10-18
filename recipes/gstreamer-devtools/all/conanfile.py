import os

from conans import *


class GStreamerDevtoolsConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
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
        "base/[^1.0.0]",
        "meson/[^0.51.2]",
    )
    requires = (
        "gstreamer-plugins-base/[^1.16]",
        "json-glib/[~1.4.4]",
    )

    def source(self):
        git = tools.Git(folder="gst-devtools")
        git.clone("https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror.git", "rebased-aivero_mse_compare_changes")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-devtools", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
