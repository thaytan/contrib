from build import *


class LibNiceRecipe(GstRecipe):
    description = "An implementation of the IETF's Interactive Connectivity Establishment (ICE) standard"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
    )
    requires = (
        "openssl1/[^1.1.1h]",
        "gst-plugins-base/[^1.18]",
    )

    def source(self):
        self.get(
            f"https://github.com/libnice/libnice/archive/{self.version}.tar.gz"
        )

    def package(self):
        self.copy("nice.pc", dst="lib/pkgconfig")

    def build(self):
        opts = {
            "gstreamer": True,
        }
        self.meson(opts)
