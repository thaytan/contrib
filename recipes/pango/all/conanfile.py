import os

from conans import *


class PangoConan(ConanFile):
    description = "A library for layout and rendering of text"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")
        self.build_requires("gobject-introspection/[^1.59.3]")

    def requirements(self):
        self.requires("fribidi/[^1.0.5]")
        self.requires("cairo/[^1.16.0]")
        self.requires("harfbuzz/[^2.6.1]")

    def source(self):
        tools.get("https://github.com/GNOME/pango/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dgtk_doc=false")
        args.append("-Dinstall-tests=false")
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
