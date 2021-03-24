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
    requires = (
        "gst-plugins-base/[^1.18]",
    )

    def source(self):
        if "1.18" in self.settings.gstreamer:
            git = tools.Git(folder=f"{self.name}-{self.version}.src")
            git.clone("https://gitlab.freedesktop.org/GStreamer/gst-rtsp-server.git", self.version)

            # Apply:  rtspclientsink: Add "update-sdp" signal that allows updating the SDP before... 
            # Not required from 1.20 onward
            # https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/commit/ac5213dcdf09f95c71329005a865a39867c3e7c1
            git.run('-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../ac5213dcdf09f95c71329005a865a39867c3e7c1.patch')

        else:
            self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/archive/{self.version}/gst-rtsp-server-{self.version}.tar.gz")

    def build(self):
        opts = {}
        opts["examples"] = self.options.examples
        opts["tests"] = self.options.tests
        opts["introspection"] = self.options.introspection
        opts["rtspclientsink"] = self.options.rtspclientsink
        self.meson(opts)