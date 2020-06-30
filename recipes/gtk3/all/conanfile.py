import os

from conans import *


class Gtk3Conan(ConanFile):
    description = "GObject-based multi-platform GUI toolkit"
    license = "LGPL-2.1"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {
        "introspection": [True, False],
        "x11": [True, False],
    }
    default_options = (
        "introspection=True",
        "x11=True",
    )

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")
        self.build_requires("gettext/[^0.20.1]")
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]",)

    def requirements(self):
        self.requires("glib/[^2.62.0]")
        self.requires("cairo/[^1.16.0]")
        self.requires("libepoxy/[^1.5.3]")
        self.requires("atk/[^2.35.1]")
        self.requires("at-spi2-atk/[^2.34.0]")
        self.requires("gdk-pixbuf/[^2.38.2]")
        self.requires("pango/[^1.43.0]")
        if self.options.x11:
            self.requires("libx11/[^1.6.8]")
            self.requires("libxkbcommon/[^0.8.4]")
            self.requires("libxrandr/[^1.5.2]")
            self.requires("libxi/[^1.7.1]")

    def source(self):
        tools.get("https://github.com/GNOME/gtk/archive/%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--auto-features=disabled",
            "--wrap-mode=nofallback",
            "-Dwayland_backend=false",
        ]
        meson = Meson(self)
        meson.configure(source_folder="gtk-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
