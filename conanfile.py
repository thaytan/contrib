from conans import ConanFile, Meson, tools

import os

class GStreamerPluginsGoodConan(ConanFile):
    name = "gstreamer-plugins-good"
    version = "1.15.1"
    default_user = "bincrafters"
    url = "https://github.com/bincrafters/conan-" + name
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = ()
    requires = (
        "glib/2.58.1@%s/stable" % self.user,
        "gstreamer/%s@%s/stable" % (version, self.user),
        "gstreamer-plugins-base/%s@%s/stable" % (version, self.user),
    )

    def source(self):
        tools.get("https://github.com/GStreamer/gst-plugins-good/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "-Dintrospection=disabled", "-Dexamples=disabled", "-Dtests=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-good-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))


