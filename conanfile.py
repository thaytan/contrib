from conans import ConanFile, Meson, tools

import os

class GStreamerPluginsBadConan(ConanFile):
    name = "gstreamer-plugins-bad"
    version = "1.15.1"
    default_user = "bincrafters"
    url = "https://github.com/bincrafters/conan-" + name
    description = "A set of plugins that aren't up to par compared to the rest"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = ()

    def requirements(self):
        self.requires("glib/2.58.1@%s/stable" % self.user)
        self.requires("gstreamer/%s@%s/stable" % (self.version, self.user))
        self.requires("gstreamer-plugins-base/%s@%s/stable" % (self.version, self.user))

    def source(self):
        tools.get("https://github.com/GStreamer/gst-plugins-bad/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "--auto-features=disabled", "-Dgl_api=opengl"]
        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-bad-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
