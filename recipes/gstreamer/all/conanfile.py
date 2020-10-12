import os

from conans import *


class GStreamerConan(ConanFile):
    name = "gstreamer"
    description = "A framework for streaming media"
    license = "LGPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    options = {
        "check": [True, False],
        "tools": [True, False],
    }
    default_options = (
        "check=True",
        "tools=True",
    )
    build_requires = (
        "meson/[^0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "glib/[^2.62.0]",
    )

    def source(self):
        git = tools.Git(folder=f"{self.name}-{self.version}")
        git.clone(
            url="https://gitlab.freedesktop.org/gstreamer/gstreamer.git", branch=self.version, shallow=True,
        )

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dcheck=" + ("enabled" if self.options.check else "disabled"))
        args.append("-Dtools=" + ("enabled" if self.options.tools else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_SCANNER = os.path.join(self.package_folder, "bin", "gstreamer-1.0", "gst-plugin-scanner")
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
