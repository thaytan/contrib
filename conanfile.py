from conans import ConanFile, Meson, tools

import os

class GStreamerConan(ConanFile):
    name = "gstreamer"
    version = "1.15.1"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/bincrafters/conan-" + name
    description = "A framework for streaming media"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "introspection": [True, False]}
    default_options = ("shared=False", "introspection=True")

    def requirements(self):
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("bison/3.0.4@%s/%s" % (self.user, self.channel), private=True)
        self.requires("flex/2.6.4@%s/%s" % (self.user, self.channel), private=True)
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/%s" % (self.user, self.channel),)

    def source(self):
        tools.get("https://github.com/GStreamer/gstreamer/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "--auto-features=disabled"]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="gstreamer-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include/gstreamer-1.0"]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
