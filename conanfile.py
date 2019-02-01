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
    options = {"shared": [True, False], "introspection": [True, False]}
    default_options = ("shared=False", "introspection=True")

    def requirements(self):
        self.requires("glib/2.58.1@%s/stable" % self.user)
        self.requires("gstreamer/%s@%s/stable" % (self.version, self.user))
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gst-plugins-base/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "-Dgtk_doc=disabled", "-Dtests=disabled", "-Dgl=enabled", "-Dgl_platform=egl"]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="gst-plugins-base-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include/gstreamer-1.0"]
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
