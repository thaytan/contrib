from conans import ConanFile, Meson, tools

import os

class GStreamerPluginsBadConan(ConanFile):
    name = "gstreamer-plugins-bad"
    version = "1.15.1"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/bincrafters/conan-" + name
    description = "A set of plugins that aren't up to par compared to the rest"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "introspection": [True, False],
        "videoparsersbad": [True, False],
        "gl": [True, False],
        "nvdec": [True, False],
        "nvenc": [True, False],
        "pnm": [True, False],
    }
    default_options = (
        "shared=False",
        "introspection=True",
        "videoparsersbad=True",
        "gl=True",
        "nvdec=True",
        "nvenc=True",
        "pnm=True",
    )
    folder_name = "gst-plugins-bad-" + version
    no_copy_source = True

    def configure(self):
        if self.settings.arch != "x86_64":
            self.options.remove("nvdec")
            self.options.remove("nvenc")

    def requirements(self):
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("gstreamer/%s@%s/%s" % (self.version, self.user, self.channel))
        self.requires("gstreamer-plugins-base/%s@%s/%s" % (self.version, self.user, self.channel))
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/GStreamer/gst-plugins-bad/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "--auto-features=disabled", "-Dgl_api=opengl"]
        args.append("-Dvideoparsersbad=" + ("enabled" if self.options.videoparsersbad else "disabled"))
        args.append("-Dgl=" + ("enabled" if self.options.gl else "disabled"))
        args.append("-Dpnm=" + ("enabled" if self.options.pnm else "disabled"))
        if self.settings.arch == "x86_64":
            args.append("-Dnvdec=" + ("enabled" if self.options.nvdec else "disabled"))
            args.append("-Dnvenc=" + ("enabled" if self.options.nvenc else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder=self.folder_name, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
