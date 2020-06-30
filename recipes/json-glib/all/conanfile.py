from conans import *


class JsonGlibBaseConan(ConanFile):
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {"introspection": [True, False]}
    default_options = "introspection=True"

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")
        self.build_requires("gettext/[^0.20.1]")
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.59.3]")

    def requirements(self):
        self.requires("glib/[^2.62.0]")

    def source(self):
        tools.get("https://gitlab.gnome.org/GNOME/json-glib/-/archive/{0}/json-glib-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dintrospection=" + ("true" if self.options.introspection else "false"))
        meson = Meson(self)
        meson.configure(args=args, source_folder="%s-%s" % (self.name, self.version))
        meson.install()
