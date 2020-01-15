import os

from conans import ConanFile, Meson, tools


class GStreamerLibavConan(ConanFile):
    name = "gstreamer-libav"
    version = tools.get_env("GIT_TAG", "1.16.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "GPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.58.1]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[~%s]@%s/stable" % (self.version, self.user))
        self.requires("ffmpeg/[>=4.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gst-libav/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-libav-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
