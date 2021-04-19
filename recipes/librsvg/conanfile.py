from build import *


class Librsvg(Recipe):
    description = "SVG rendering library"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "gobject-introspection/[^1.68.0]",
        "rust/[^1.0.0]",
        "gtk-doc/[^1.33.2]",
    )
    requires = (
        "pango/[^1.48.4]",
        ("gdk-pixbuf2-no-librsvg/[^2.42.6]", "private"),
        ("libxml2/[^2.9.10]", "private"),
        ("shared-mime-info/[^2.0]", "private"),
        # ("libx11/[^1.6.8]", "private")
        # ("libpng/[^1.6.37]", "private")
        # ("libjpeg-turbo/[^2.0.5]", "private")
    )

    def source(self):
        self.get(f"https://github.com/GNOME/librsvg/archive/refs/tags/{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-pixbuf-loader",
        ]
        self.autotools(args)
