from build import *


class GstRtspServerRecipe(GstRecipe):
    description = "A framework for streaming media"
    license = "LGPL"
    exports = "*.patch"
    options = {
        "examples": [True, False],
        "tests": [True, False],
        "introspection": [True, False],
        "rtspclientsink": [True, False],
    }
    default_options = (
        "examples=False",
        "tests=False",
        "introspection=True",
        "rtspclientsink=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.51.2]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        "gobject-introspection/[^1.59.3]",
    )

    def requirements(self):
        self.requires(f"gst-plugins-base/[~{self.settings.gstreamer}]")

    def source(self):
        if "1.19" in self.version:
            git = tools.Git(folder=f"{self.name}-{self.version}.src")
            git.clone("https://gitlab.freedesktop.org/gstreamer/gstreamer.git", "main")
            git.run("checkout 14d636b224f3f00779ccb165750c29f8b69eb34d")

    def build(self):
        opts = {}
        opts["examples"] = self.options.examples
        opts["tests"] = self.options.tests
        opts["introspection"] = self.options.introspection
        opts["rtspclientsink"] = self.options.rtspclientsink
        self.meson(
            opts=opts, source_folder=os.path.join(self.src, "subprojects", "gst-rtsp-server")
        )
