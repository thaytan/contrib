import os

from conans import *


class AtkConan(ConanFile):
    description = "GObject-based multi-platform GUI toolkit"
    license = "LGPL-2.1"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "meson/[^0.51.2]",
        "gettext/[^0.20.1]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "glib/[^2.62.0]",
    )

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/atk/-/archive/ATK_{self.version}/atk-ATK_{self.version.replace(".", "_")}.tar.bz2")

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(source_folder="atk-ATK_" + self.version.replace(".", "_"), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
