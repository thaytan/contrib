import os
from conans import *


class AtkConan(ConanFile):
    description = "GObject-based multi-platform GUI toolkit"
    license = "LGPL-2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {
        "introspection": [True, False],
    }
    default_options = ("introspection=True",)
    build_requires = (
        "meson/[^0.55.3]",
        "gettext/[^0.21]",
    )
    requires = ("glib/[^2.66.1]",)

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]",)

    def source(self):
        version = self.version.replace(".", "_")
        tools.get(f"https://gitlab.gnome.org/GNOME/atk/-/archive/ATK_{version}/atk-ATK_{version}.tar.bz2")

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(args, source_folder=f"atk-ATK_{self.version.replace('.', '_')}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
