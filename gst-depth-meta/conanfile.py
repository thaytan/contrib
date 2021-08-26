from build import *

class GstDepthMeta(GstProject):
    license = "Apache"
    description = "Library to stream depth video"
    exports_sources = (
        "meson.build", 
        "src/*"
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.57.2]"
    )
    requires = (
        "gst-plugins-base/[^1.18]"
    )

    def source(self):
        self.run("mkdir gst-depth-meta")
        self.run("mv src gst-depth-meta/")
        self.run("mv meson.build.conan gst-depth-meta/meson.build")

    def build(self):
        self.meson(source_folder="gst-depth-meta")

