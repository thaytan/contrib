from conans import ConanFile, Meson, tools

import os

class GStreamerLibavConan(ConanFile):
    name = "gstreamer-libav"
    version = "1.16.0"
    default_user = "bincrafters"
    url = "https://github.com/bincrafters/conan-" + name
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = "fPIC=True"

    def requirements(self):
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("ffmpeg/4.1@%s/%s" % (self.user, self.channel))
        self.requires("gstreamer/%s@%s/%s" % (self.version, self.user, self.channel))
        self.requires("gstreamer-plugins-base/%s@%s/%s" % (self.version, self.user, self.channel))

    def source(self):
        tools.get("https://github.com/GStreamer/gst-libav/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-libav-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
