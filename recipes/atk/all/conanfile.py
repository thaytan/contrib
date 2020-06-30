import os

from conans import *


class AtkConan(ConanFile):
    description = "GObject-based multi-platform GUI toolkit"
    license = "LGPL-2.1"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {
        "introspection": [True, False],
    }
    default_options = ("introspection=True",)
    build_requires = (
        "generators/1.0.0",
        "meson/[^0.51.2]",
        "gettext/[^0.20.1]",
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]",)
    )
    requires = (
        "glib/[^2.62.0]",
    )

    def source(self):
        tools.get("https://gitlab.gnome.org/GNOME/atk/-/archive/ATK_{0}/atk-ATK_{0}.tar.bz2".format(self.version.replace(".", "_")))

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(source_folder="atk-ATK_" + self.version.replace(".", "_"), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
