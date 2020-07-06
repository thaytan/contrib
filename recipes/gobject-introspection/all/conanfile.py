import os

from conans import *


class GObjectIntrospectionConan(ConanFile):
    description = "Middleware layer between C libraries (using GObject) and language bindings"
    license = "GPL, LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "meson/[^0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
    )
    requires = (
        "base/[^1.0.0]",
        "python/[^3.7.4]",
        "glib/[^2.62.0]",
    )

    def source(self):
        tools.get(f"https://github.com/GNOME/gobject-introspection/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "gobject-introspection")
