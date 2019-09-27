from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.16.0"
    except:
        return None

class GStreamerLibavConan(ConanFile):
    name = "gstreamer-libav"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=0.1]@%s/stable" % self.user)
        self.requires("glib/[>=2.58.1]@%s/stable" % self.user)
        self.requires("ffmpeg/[>=4.1]@%s/stable" % self.user)
        self.requires("gstreamer/%s@%s/stable" % (self.version, self.user))
        self.requires("gstreamer-plugins-base/%s@%s/stable" % (self.version, self.user))

    def source(self):
        tools.get("https://github.com/GStreamer/gst-libav/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-libav-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
