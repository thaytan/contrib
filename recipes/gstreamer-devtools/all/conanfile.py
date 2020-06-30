import os

from conans import *


class GStreamerDevtoolsConan(ConanFile):
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {
        "gtk_doc": [True, False],
        "introspection": [True, False],
        "tests": [True, False],
        "nls": [True, False],
    }
    default_options = "gtk_doc=False", "introspection=False", "tests=True", "nls=False"
    gst_version = "[~1]"

    def build_requirements(self):
        self.build_requires("generators/[^1.0.0]")
        self.build_requires("meson/[^0.51.2]")

    def source(self):
        git = tools.Git(folder="gst-devtools")
        git.clone("https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror.git", "rebased-aivero_mse_compare_changes")

    def requirements(self):
        self.requires("gstreamer-plugins-base/%s" % (self.gst_version))
        self.requires("json-glib/[~1.4.4]")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-devtools", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
