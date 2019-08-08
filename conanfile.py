from conans import ConanFile, Meson, tools

import os

class JsonGlibBaseConan(ConanFile):
    name = "json-glib"
    version = "1.4.4"
    url = "https://github.com/bincrafters/conan-" + name
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "introspection": [True, False],
    }
    default_options = (
        "introspection=True",
    )

    def requirements(self):
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/%s" % (self.user, self.channel),)

    def source(self):
        tools.get("https://github.com/GNOME/json-glib/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dintrospection=" + ("true" if self.options.introspection else "false"))

        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
