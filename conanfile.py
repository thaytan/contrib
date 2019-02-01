from conans import ConanFile, Meson, tools

import os

class GStreamerLibavConan(ConanFile):
    name = "gstreamer-libav"
    version = "1.15.1"
    default_user = "bincrafters"
    url = "https://github.com/bincrafters/conan-" + name
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = ()

    def requirements(self):
        self.requires("glib/2.58.1@%s/stable" % self.user)
        self.requires("ffmpeg/4.1@%s/stable" % self.user)
        self.requires("gstreamer/%s@%s/stable" % (version, self.user))

    def source(self):
        tools.get("https://github.com/GStreamer/gst-libav/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib"]
        meson = Meson(self)
        meson.configure(source_folder="gst-libav-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
