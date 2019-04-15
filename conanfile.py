from conans import ConanFile, Meson, tools

import os

class GStreamerPluginsBaseConan(ConanFile):
    name = "gstreamer-plugins-base"
    version = "1.15.1"
    default_user = "bincrafters"
    url = "https://github.com/bincrafters/conan-" + name
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
        "orc": [True, False],
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
        "orc=True",
    )
    folder_name = "gst-plugins-base-" + version

    def requirements(self):
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("gstreamer/%s@%s/%s" % (self.version, self.user, self.channel))
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/%s" % (self.user, self.channel))
        if self.options.orc:
            self.requires("orc/0.4.29@%s/%s" % (self.user, self.channel))

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
        args.append("-Dorc=" + ("enabled" if self.options.orc else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder=self.folder_name, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.includedirs = ["include/gstreamer-1.0"]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
