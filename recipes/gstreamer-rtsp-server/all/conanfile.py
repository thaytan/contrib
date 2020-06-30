import os

from conans import *


class GStreamerRtspServerConan(ConanFile):
    description = "A framework for streaming media"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {
        "examples": [True, False],
        "tests": [True, False],
        "introspection": [True, False],
        "rtspclientsink": [True, False],
    }
    default_options = (
        "examples=False",
        "tests=False",
        "introspection=True",
        "rtspclientsink=True",
    )
    build_requires = (
        "generators/1.0.0",
        "meson/[^0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]")
    )
    requires = (
        "glib/[^2.62.0]",
        "gstreamer/[~%s]" % (self.version),
        "gstreamer-plugins-base/[~%s]" % (self.version),

    def source(self):
        tools.get("https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/archive/%s/gst-rtsp-server-%s.tar.gz" % (self.version, self.version))

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dcheck=" + ("enabled" if self.options.examples else "disabled"))
        args.append("-Dtools=" + ("enabled" if self.options.tests else "disabled"))
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Drtspclientsink=" + ("enabled" if self.options.rtspclientsink else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="gst-rtsp-server-%s" % self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
