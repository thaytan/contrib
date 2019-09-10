from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.16.0"
    except:
        return None

class GStreamerPluginsBaseConan(ConanFile):
    name = "gstreamer-plugins-base"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "introspection": [True, False],
        "gl": [True, False],
        "x11": [True, False],
        "videotestsrc": [True, False],
        "videoconvert": [True, False],
        "app": [True, False],
        "playback": [True, False],
        "typefind": [True, False],
        "timeoverlay": [True, False],
        "orc": [True, False],
        "opus": [True, False],
    }
    default_options = (
        "introspection=True",
        "gl=True",
        "x11=True",
        "videotestsrc=True",
        "videoconvert=True",
        "app=True",
        "playback=True",
        "typefind=True",
        "timeoverlay=True",
        "orc=True",
        "opus=True",
    )
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("glib/2.58.1@%s/stable" % self.user)
        self.requires("gstreamer/%s@%s/stable" % (self.version, self.user))
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/stable" % self.user)
        if self.options.orc:
            self.requires("orc/0.4.29@%s/stable" % self.user)
        if self.options.opus:
            self.requires("opus/1.3.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gst-plugins-base/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "-Dgl_platform=egl"]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Dgl=" + ("enabled" if self.options.gl else "disabled"))
        args.append("-Dx11=" + ("enabled" if self.options.x11 else "disabled"))
        args.append("-Dvideotestsrc=" + ("enabled" if self.options.videotestsrc else "disabled"))
        args.append("-Dvideoconvert=" + ("enabled" if self.options.videoconvert else "disabled"))
        args.append("-Dapp=" + ("enabled" if self.options.app else "disabled"))
        args.append("-Dplayback=" + ("enabled" if self.options.playback else "disabled"))
        args.append("-Dtypefind=" + ("enabled" if self.options.typefind else "disabled"))
        args.append("-Dtimeoverlay=" + ("enabled" if self.options.timeoverlay else "disabled"))
        args.append("-Dorc=" + ("enabled" if self.options.orc else "disabled"))
        args.append("-Dopus=" + ("enabled" if self.options.opus else "disabled"))
        self.run("env")
        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-base-" + self.version, args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.includedirs = ["include/gstreamer-1.0"]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
