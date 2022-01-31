from build import *


class Vala(Recipe):
    description = "Compiler for the GObject type system"
    license = "LGPL"
    build_requires = (
        "libxslt/[^1.1.34]",
    )
    requires = (
        "autotools/[^1.0.0]",
        "cc/[^1.0.0]",
        "glib/[^2.68.4]",
    )

    def source(self):
        self.get(f"https://gitlab.gnome.org/GNOME/vala/-/archive/{self.version}/vala-{self.version}.zip")