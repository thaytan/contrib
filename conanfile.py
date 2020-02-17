import os

from conans import ConanFile, Meson, tools

class GStreamerPluginsGoodConan(ConanFile):
    name = "gstreamer-plugins-good"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "autodetect": [True, False],
        "rtp": [True, False],
        "rtsp": [True, False],
        "udp": [True, False],
        "png": [True, False],
        "isomp4": [True, False],
        "videofilter": [True, False],
        "vpx": [True, False],
        "multifile": [True, False],
        "matroska": [True, False],
        "videomixer": [True, False],
        "ximagesrc": [True, False],
        "ximagesrc_xdamage": [True, False],
        "ximagesrc_xshm": [True, False],
        "jpeg": [True, False]

    }
    default_options = (
        "autodetect=True",
        "rtp=True",
        "rtsp=True",
        "udp=True",
        "png=True",
        "isomp4=True",
        "videofilter=True",
        "vpx=True",
        "multifile=True",
        "matroska=True",
        "videomixer=True",
        "ximagesrc=True",
        "ximagesrc_xdamage=False",
        "ximagesrc_xshm=True",
        "jpeg=True"
    )

    def set_version(self):
        git = tools.Git(folder=self.recipe_folder)
        tag, branch = git.get_tag(), git.get_branch()
        self.version = tag if tag and branch.startswith("HEAD") else branch

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        gst_version = "master" if self.version == "master" else "[~%s]" % self.version
        gst_channel = "testing" if self.version == "master" else "stable"
        self.requires("gstreamer-plugins-base/%s@%s/%s" % (gst_version, self.user, gst_channel))
        self.requires("libpng/[>=1.6.37]@%s/stable" % self.user)
        if self.options.vpx:
            self.requires("libvpx/[>=1.8.0]@%s/stable" % self.user)
        if self.options.jpeg:
            self.requires("libjpeg-turbo/[>=2.0.3]@%s/stable" % self.user)

    def source(self):
        git = tools.Git(folder="gst-plugins-good-" + self.version)
        plugins_bad_branch = "master" if self.version == "master" else "splitmuxsink-muxerpad-map-1.16.0"
        git.clone("https://gitlab.freedesktop.org/thaytan/gst-plugins-good", plugins_bad_branch)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dautodetect=" + ("enabled" if self.options.autodetect else "disabled"))
        args.append("-Drtp=" + ("enabled" if self.options.rtp else "disabled"))
        args.append("-Drtsp=" + ("enabled" if self.options.rtsp else "disabled"))
        args.append("-Drtpmanager=" + ("enabled" if self.options.rtp else "disabled"))
        args.append("-Dudp=" + ("enabled" if self.options.udp else "disabled"))
        args.append("-Dpng=" + ("enabled" if self.options.png else "disabled"))
        args.append("-Disomp4=" + ("enabled" if self.options.isomp4 else "disabled"))
        args.append("-Dvideofilter=" + ("enabled" if self.options.videofilter else "disabled"))
        args.append("-Dvpx=" + ("enabled" if self.options.vpx else "disabled"))
        args.append("-Dmultifile=" + ("enabled" if self.options.multifile else "disabled"))
        args.append("-Dmatroska=" + ("enabled" if self.options.matroska else "disabled"))
        args.append("-Dvideomixer=" + ("enabled" if self.options.videomixer else "disabled"))
        args.append("-Dximagesrc=" + ("enabled" if self.options.ximagesrc else "disabled"))
        args.append("-Dximagesrc-xdamage=" + ("enabled" if self.options.ximagesrc_xdamage else "disabled"))
        args.append("-Dxshm=" + ("enabled" if self.options.ximagesrc_xshm else "disabled"))
        args.append("-Djpeg=" + ("enabled" if self.options.jpeg else "disabled"))

        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-good-%s" % self.version, args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
