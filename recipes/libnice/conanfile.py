from build import *


class LibNiceRecipe(GstreamerRecipe):
    description = "An implementation of the IETF's Interactive Connectivity Establishment (ICE) standard"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]", 
        "meson/[^0.55.3]",
    )
    requires = (
        "openssl1/[^1.1.1h]",
        "gst-plugins-base/[^1.18.1]",
    )

    def source(self):
        self.get(f"https://github.com/libnice/libnice/archive/{self.version}.tar.gz")

    def build(self):
        opts = {
            "gstreamer": True,
        }
        self.meson(opts)
