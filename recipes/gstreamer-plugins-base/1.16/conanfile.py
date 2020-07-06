import os

from conans import *


class GStreamerPluginsBaseConan(ConanFile):
    name = "gstreamer-plugins-base"
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "LGPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    options = {
        "introspection": [True, False],
        "gl": [True, False],
        "x11": [True, False],
        "videotestsrc": [True, False],
        "audiotestsrc": [True, False],
        "videoconvert": [True, False],
        "app": [True, False],
        "playback": [True, False],
        "typefind": [True, False],
        "timeoverlay": [True, False],
        "orc": [True, False],
        "opus": [True, False],
        "pango": [True, False],
        "audioconvert": [True, False],
        "videoscale": [True, False],
        "audioresample": [True, False],
    }
    default_options = (
        "introspection=True",
        "gl=True",
        "x11=True",
        "videotestsrc=True",
        "audiotestsrc=True",
        "videoconvert=True",
        "app=True",
        "playback=True",
        "typefind=True",
        "timeoverlay=True",
        "orc=True",
        "opus=True",
        "pango=True",
        "audioconvert=True",
        "videoscale=True",
        "audioresample=False",
    )
    build_requires = (
        "meson/[^0.51.2]",
        "mesa/[^19.2.0]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "base/[^1.0.0]",
        "gstreamer/[~1.16]",
    )

    def requirements(self):
        if self.options.orc:
            self.requires("orc/[^0.4.29]")
        if self.options.opus:
            self.requires("opus/[^1.3.1]")
        if self.options.pango:
            self.requires("pango/[^1.43.0, include_prerelease=True]")
        if self.options.x11:
            self.requires("libx11/[^1.6.8]")

    def source(self):
        git = tools.Git(folder="gst-plugins-base-" + self.version)
        git.clone(url="https://gitlab.freedesktop.org/gstreamer/gst-plugins-base.git", branch=self.version, shallow=True)

    def build(self):
        args = ["--auto-features=disabled", "-Dgl_platform=egl"]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Dgl=" + ("enabled" if self.options.gl else "disabled"))
        args.append("-Dx11=" + ("enabled" if self.options.x11 else "disabled"))
        args.append("-Dvideotestsrc=" + ("enabled" if self.options.videotestsrc else "disabled"))
        args.append("-Daudiotestsrc=" + ("enabled" if self.options.audiotestsrc else "disabled"))
        args.append("-Dvideoconvert=" + ("enabled" if self.options.videoconvert else "disabled"))
        args.append("-Dapp=" + ("enabled" if self.options.app else "disabled"))
        args.append("-Dplayback=" + ("enabled" if self.options.playback else "disabled"))
        args.append("-Dtypefind=" + ("enabled" if self.options.typefind else "disabled"))
        args.append("-Dorc=" + ("enabled" if self.options.orc else "disabled"))
        args.append("-Dopus=" + ("enabled" if self.options.opus else "disabled"))
        args.append("-Dpango=" + ("enabled" if self.options.pango else "disabled"))
        args.append("-Daudioresample=" + ("enabled" if self.options.audiotestsrc else "disabled"))
        args.append("-Dvideoscale=" + ("enabled" if self.options.videoscale else "disabled"))
        args.append("-Daudioconvert=" + ("enabled" if self.options.audioconvert else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-base-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
