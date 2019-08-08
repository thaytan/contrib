from conans import ConanFile, Meson, tools

import os

class GStreamerPluginsBadConan(ConanFile):
    name = "gstreamer-plugins-bad"
    version = "1.16.0"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A set of plugins that aren't up to par compared to the rest"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    exports = "reduce_latency.patch"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "introspection": [True, False],
        "videoparsers": [True, False],
        "gl": [True, False],
        "nvdec": [True, False],
        "nvenc": [True, False],
        "pnm": [True, False],
        "webrtc": [True, False],
        "srtp": [True, False],
        "dtls": [True, False],
        "mpegtsmux": [True, False],
        "mpegtsdemux": [True, False],
        "debugutils": [True, False]
    }
    default_options = (
        "introspection=True",
        "videoparsers=True",
        "gl=True",
        "nvdec=False",
        "nvenc=False",
        "pnm=True",
        "webrtc=True",
        "srtp=True",
        "dtls=True",
        "mpegtsmux=True",
        "mpegtsdemux=True",
        "debugutils=True",
    )
    generators = "env"

    def configure(self):
        if self.settings.arch != "x86_64":
            self.options.remove("nvdec")
            self.options.remove("nvenc")

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("gstreamer/%s@%s/%s" % (self.version, self.user, self.channel))
        self.requires("gstreamer-plugins-base/%s@%s/%s" % (self.version, self.user, self.channel))
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/%s" % (self.user, self.channel))
        if self.options.webrtc:
            self.requires("libnice/0.1.15@%s/%s" % (self.user, self.channel))
        if self.options.srtp:
            self.requires("libsrtp/2.2.0@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/GStreamer/gst-plugins-bad/archive/%s.tar.gz" % self.version)
        tools.patch(patch_file="reduce_latency.patch", base_path=os.path.join(self.source_folder, "gst-plugins-bad-" + self.version))

    def build(self):
        args = ["--auto-features=disabled", "-Dgl_api=opengl"]
        args.append("-Dvideoparsers=" + ("enabled" if self.options.videoparsers else "disabled"))
        args.append("-Dgl=" + ("enabled" if self.options.gl else "disabled"))
        args.append("-Dpnm=" + ("enabled" if self.options.pnm else "disabled"))
        args.append("-Dwebrtc=" + ("enabled" if self.options.webrtc else "disabled"))
        args.append("-Dsrtp=" + ("enabled" if self.options.srtp else "disabled"))
        args.append("-Ddtls=" + ("enabled" if self.options.srtp else "disabled"))
        args.append("-Dmpegtsmux=" + ("enabled" if self.options.mpegtsmux else "disabled"))
        args.append("-Dmpegtsdemux=" + ("enabled" if self.options.mpegtsdemux else "disabled"))
        args.append("-Ddebugutils=" + ("enabled" if self.options.debugutils else "disabled"))

        if self.settings.arch == "x86_64":
            args.append("-Dnvdec=" + ("enabled" if self.options.nvdec else "disabled"))
            args.append("-Dnvenc=" + ("enabled" if self.options.nvenc else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-bad-" + self.version, args=args)
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
