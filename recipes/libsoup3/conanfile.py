from build import *


class Libsoup3(Recipe):
    description = "HTTP client/server library for GNOME"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "gobject-introspection/[^1.69.0]",
        #"python/[^3.10.2]",
        #"vala/[^0.54.6]",
        #"git/[^2.35.0]",
        #"gtk-doc/[^1.33.2]",
        "meson/[>=0.57.2]",
        #"samba/[^4.15.4]",
        #"python-quart/[^0.16.2]",
    )
    requires = (
        "glib/[^2.68.4]",
        #"glib-networking/[^2.70.1]",
        #"sqlite/[^3.37.2]",
        #"krb5/[^1.19.2]",
        #"libpsl/[^0.21.1]",
        #"brotli/[^1.0.9]",
        #"libnghttp2/[^1.46.0]",
    )

    def source(self):
        self.get(f"https://gitlab.gnome.org/GNOME/libsoup/-/archive/{self.version}/libsoup-{self.version}.tar.gz")

    
    def build(self):
        self.run("meson introspect --buildoptions libsoup3-3.0.4.src/meson.build")
        #self.meson()