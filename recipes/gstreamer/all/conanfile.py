import os
from conans import *


class GStreamerConan(ConanFile):
    description = "A framework for streaming media"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    build_requires = (
        "clang/[^10.0.1]",
        "meson/[^0.55.3]",
        "bison/[^3.7.2]",
        "flex/[^2.6.4]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = ("glib/[^2.62.0]",)

    def source(self):
        tools.get(f"https://github.com/GStreamer/gstreamer/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dcheck=enabled",
            "-Dtools=enabled",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"gstreamer-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_SCANNER = os.path.join(self.package_folder, "bin", "gstreamer-1.0", "gst-plugin-scanner")
