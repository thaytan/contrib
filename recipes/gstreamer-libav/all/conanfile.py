import os

from conans import ConanFile, Meson, tools


class GStreamerLibavConan(ConanFile):
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")

    def requirements(self):
        self.requires("glib/[^2.58.1]")
        self.requires("gstreamer-plugins-base/[~%s]" % (self.version))
        self.requires("ffmpeg/[^4.1]")

    def source(self):
        tools.get("https://github.com/GStreamer/gst-libav/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-libav-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
