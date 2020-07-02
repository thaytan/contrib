from conans import *


class JsonGlibBaseConan(ConanFile):
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "meson/[^0.51.2]",
        "gettext/[^0.20.1]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "generators/[^1.0.0]",
        "glib/[^2.62.0]",
    )

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/json-glib/-/archive/{self.version}/json-glib-{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(args=args, source_folder=f"{self.name}-{self.version}")
        meson.install()
