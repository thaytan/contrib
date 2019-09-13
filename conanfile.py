from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.15.1"
    except:
        return None

class JsonGlibBaseConan(ConanFile):
    name = "json-glib"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {"introspection": [True, False]}
    default_options = "introspection=True"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("glib/2.58.1@%s/stable" % self.user)
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GNOME/json-glib/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dintrospection=" + ("true" if self.options.introspection else "false"))

        meson = Meson(self)
        meson.configure(args=args, source_folder="%s-%s" % (self.name, self.version))
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
