import os

from conans import *


class GStreamerPythonConan(ConanFile):
    description = "Gstreamer Python bindings"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")

    def requirements(self):
        self.requires("gstreamer/%s" % (self.version))
        self.requires("gobject-introspection/1.59.3")
        self.requires("python-gobject/3.33.1")

    def source(self):
        tools.get("https://github.com/GStreamer/gst-python/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-python-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3.7", "site-packages")
