import os
from conans import ConanFile, Meson, tools

class GStreamerPluginsBaseConan(ConanFile):
    name = "gstreamer-plugins-base"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "LGPL"
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
        "pango": [True, False],
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
        "pango=True",
    )
    generators ="pkgconf"

    def set_version(self):
        git = tools.Git(folder=self.recipe_folder)
        tag, branch = git.get_tag(), git.get_branch()
        self.version = tag if tag and branch.startswith("HEAD") else branch

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("mesa/[>=19.2.0]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        gst_version = "master" if self.version == "master" else "[~%s]" % self.version
        gst_channel = "testing" if self.version == "master" else "stable"
        self.requires("gstreamer/%s@%s/%s" % (gst_version, self.user, gst_channel))
        if self.options.orc:
            self.requires("orc/[>=0.4.29]@%s/stable" % self.user)
        if self.options.opus:
            self.requires("opus/[>=1.3.1]@%s/stable" % self.user)
        if self.options.pango:
            self.requires("pango/[>=1.43.0, include_prerelease=True]@%s/stable" % self.user)
        if self.options.x11:
            self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)

    def source(self):
        git = tools.Git(folder="gst-plugins-base-" + self.version)
        git.clone(url="https://gitlab.freedesktop.org/gstreamer/gst-plugins-base.git", branch=self.version, shallow=True)

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
        args.append("-Dorc=" + ("enabled" if self.options.orc else "disabled"))
        args.append("-Dopus=" + ("enabled" if self.options.opus else "disabled"))
        args.append("-Dpango=" + ("enabled" if self.options.pango else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-base-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
