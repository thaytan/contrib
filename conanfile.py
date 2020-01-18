import os
from conans import ConanFile, Meson, tools

def get_version():
    try:
        git = tools.Git()
        tag, branch = git.get_tag(), git.get_branch()
        return tag if tag and branch.startswith("HEAD") else branch
    except:
        return tools.get_env("GIT_BRANCH", "master")

class GStreamerPluginsBadConan(ConanFile):
    name = "gstreamer-plugins-bad"
    version = get_version()
    gst_version = "master" if version == "master" else "[~%s]" % version
    gst_channel = "testing" if version == "master" else "stable"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A set of plugins that aren't up to par compared to the rest"
    license = "LGPL"
    exports = "reduce_latency.patch"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "introspection": [True, False],
        "videoparsers": [True, False],
        "gl": [True, False],
        "nvdec": [True, False],
        "nvenc": [True, False],
        "nvcodec": [True, False],
        "pnm": [True, False],
        "webrtc": [True, False],
        "srtp": [True, False],
        "dtls": [True, False],
        "mpegtsmux": [True, False],
        "mpegtsdemux": [True, False],
        "debugutils": [True, False],
        "opencv": [True, False],
        "closedcaption": [True, False],
        "aiveropatchlatency": [True, False],
    }
    default_options = (
        "introspection=True",
        "videoparsers=True",
        "gl=True",
        "nvdec=False",
        "nvenc=False",
        "nvcodec=False",
        "pnm=True",
        "webrtc=True",
        "srtp=True",
        "dtls=True",
        "mpegtsmux=True",
        "mpegtsdemux=True",
        "debugutils=True",
        "opencv=False",
        "closedcaption=False",
        "aiveropatchlatency=False",
    )
    generators = "env"

    def configure(self):
        if self.settings.arch != "x86_64":
            self.options.remove("nvdec")
            self.options.remove("nvenc")
            self.options.remove("nvcodec")

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/%s@%s/%s" % (self.gst_version, self.user, self.gst_channel))
        if self.options.webrtc:
            libnice_version = "master" if self.version == "master" else "[>=%s]" % "0.1.15"
            self.requires("libnice/%s@%s/%s" % (libnice_version, self.user, self.gst_channel))
        if self.options.srtp:
            self.requires("libsrtp/[>=2.2.0]@%s/stable" % self.user)
        if self.options.opencv:
            self.requires("opencv/[>=3.4.8]@%s/stable" % self.user)
        if self.options.closedcaption:
            self.requires("pango/[>=1.4.3]@%s/stable" % self.user)
        if self.settings.arch == "x86_64" and (self.options.nvenc or self.options.nvdec):
            self.requires("cuda/[>=10.1 <10.2]@%s/testing" % self.user)
            self.requires("orc/[>=0.4.31]@%s/stable" % self.user)

    def source(self):
        git = tools.Git()
        git.clone(url="https://github.com/GStreamer/gst-plugins-bad.git", branch=self.version, shallow=True)
        if self.options.aiveropatchlatency:
            tools.patch(patch_file="reduce_latency.patch", base_path=os.path.join(self.source_folder, "gst-plugins-bad"))

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
        args.append("-Dopencv=" + ("enabled" if self.options.opencv else "disabled"))
        args.append("-Dclosedcaption=" + ("enabled" if self.options.closedcaption else "disabled"))
        if self.settings.arch == "x86_64":
            args.append("-Dnvdec=" + ("enabled" if self.options.nvdec else "disabled"))
            args.append("-Dnvenc=" + ("enabled" if self.options.nvenc else "disabled"))
            if self.version == "master":
                args.append("-Dnvcodec=" + ("enabled" if self.options.nvcodec else "disabled"))

        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-bad", args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
